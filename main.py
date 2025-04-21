"""
Main module for AutiConnect Telegram Bot with AI mediators.
Handles all bot commands, conversation flows, and AI-mediated interactions.
"""

import os
import logging
import json
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ConversationHandler, CallbackQueryHandler, ContextTypes
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database connection
class Database:
    def __init__(self):
        """Initialize database connection using environment variables."""
        # This is a placeholder for MongoDB connection
        # In a real implementation, this would connect to MongoDB
        self.users = {}
        self.groups = {}
        self.activities = {}
        self.messages = []
        
    def create_user(self, user_id, name, role, **kwargs):
        """Create a new user in the database."""
        try:
            # Base user data
            user_data = {
                "user_id": user_id,
                "name": name,
                "role": role,
                "groups": [],
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }
            
            # Add expanded profile information if provided
            if role == 'autista':
                # Default values for autistic user profile
                profile = {
                    "age": kwargs.get("age", None),
                    "gender": kwargs.get("gender", None),
                    "emergency_contacts": kwargs.get("emergency_contacts", []),
                    "academic_history": kwargs.get("academic_history", ""),
                    "professionals": kwargs.get("professionals", []),
                    "interests": kwargs.get("interests", []),
                    "anxiety_triggers": kwargs.get("anxiety_triggers", []),
                    "communication_preferences": kwargs.get("communication_preferences", {
                        "style": "direct",  # or "detailed"
                        "preferred_topics": [],
                        "avoided_topics": [],
                        "notes": ""
                    }),
                    "interaction_history": []
                }
                user_data["profile"] = profile
            
            # Store user
            self.users[user_id] = user_data
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile information."""
        try:
            if user_id not in self.users:
                return False
                
            # Update profile fields
            if "profile" not in self.users[user_id]:
                self.users[user_id]["profile"] = {}
                
            for key, value in profile_data.items():
                self.users[user_id]["profile"][key] = value
                
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    def get_user(self, user_id):
        """Get user information from database."""
        return self.users.get(user_id)
    
    def create_group(self, group_id, name, theme, description, created_by, max_members=10):
        """Create a new thematic group."""
        try:
            group_data = {
                "group_id": group_id,
                "name": name,
                "theme": theme,
                "description": description,
                "created_by": created_by,
                "members": [created_by],  # Creator is first member
                "max_members": max_members,
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "ai_mediator_enabled": True  # Enable AI mediator by default
            }
            
            # Store group
            self.groups[group_id] = group_data
            
            # Add group to creator's groups
            if created_by in self.users:
                self.users[created_by]["groups"].append(group_id)
            
            return True
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            return False
    
    def get_all_groups(self):
        """Get all available groups."""
        return list(self.groups.values())
    
    def get_group(self, group_id):
        """Get group information."""
        return self.groups.get(group_id)
    
    def add_user_to_group(self, user_id, group_id):
        """Add a user to a group."""
        try:
            if group_id not in self.groups or user_id not in self.users:
                return False
                
            # Add user to group's members
            if user_id not in self.groups[group_id]["members"]:
                self.groups[group_id]["members"].append(user_id)
            
            # Add group to user's groups
            if group_id not in self.users[user_id]["groups"]:
                self.users[user_id]["groups"].append(group_id)
            
            return True
        except Exception as e:
            logger.error(f"Error adding user to group: {e}")
            return False
    
    def create_activity(self, group_id, activity_type, title, description, created_by, scheduled_time=None, duration=60):
        """Create a new activity for a group."""
        try:
            activity_id = str(datetime.now().timestamp())
            
            activity_data = {
                "activity_id": activity_id,
                "group_id": group_id,
                "type": activity_type,
                "title": title,
                "description": description,
                "created_by": created_by,
                "participants": [],
                "status": "scheduled",
                "scheduled_time": scheduled_time or datetime.now(),
                "duration": duration,
                "created_at": datetime.now(),
                "ai_guidance_enabled": True  # Enable AI guidance by default
            }
            
            # Store activity
            self.activities[activity_id] = activity_data
            
            return activity_id
        except Exception as e:
            logger.error(f"Error creating activity: {e}")
            return None
    
    def get_user_activities(self, user_id):
        """Get activities for groups that a user is part of."""
        try:
            if user_id not in self.users:
                return []
                
            user_groups = self.users[user_id]["groups"]
            activities = []
            
            for activity_id, activity in self.activities.items():
                if activity["group_id"] in user_groups and activity["status"] == "scheduled":
                    activities.append(activity)
            
            return activities
        except Exception as e:
            logger.error(f"Error getting user activities: {e}")
            return []
    
    def update_last_active(self, user_id):
        """Update user's last active timestamp."""
        if user_id in self.users:
            self.users[user_id]["last_active"] = datetime.now()

# LLM Integration
class LLMIntegration:
    def __init__(self):
        """Initialize LLM integration."""
        self.api_key = os.environ.get('LLM_API_KEY')
        
    def mediate_group_conversation(self, group_id, recent_messages, current_user_id):
        """Generate AI mediator response for group conversation."""
        # This is a placeholder for actual LLM integration
        # In a real implementation, this would call the LLM API
        
        # For MVP, return a simple response
        responses = [
            "Que discussão interessante! Alguém mais gostaria de compartilhar sua experiência?",
            "Obrigado por compartilhar. Isso me faz pensar em como diferentes perspectivas enriquecem nossa conversa.",
            "Vamos explorar esse tópico um pouco mais. Alguém tem alguma pergunta sobre o que foi compartilhado?",
            "Esse é um ponto muito interessante! Como isso se relaciona com suas experiências pessoais?",
            "Parece que temos opiniões diversas aqui. Isso é ótimo para ampliar nossa compreensão do assunto."
        ]
        
        import random
        return random.choice(responses), False
    
    def provide_individual_support(self, user_id, message_text):
        """Generate AI support response for individual conversation."""
        # This is a placeholder for actual LLM integration
        # In a real implementation, this would call the LLM API
        
        # For MVP, return a simple response
        responses = [
            "Entendo como você está se sentindo. Quer conversar mais sobre isso?",
            "Obrigado por compartilhar. É normal sentir-se assim às vezes. Como posso ajudar?",
            "Estou aqui para ouvir. Quer me contar mais sobre o que está acontecendo?",
            "Isso parece desafiador. Vamos pensar juntos em algumas estratégias que possam ajudar.",
            "Sua experiência é válida e importante. Como você tem lidado com isso até agora?"
        ]
        
        import random
        return random.choice(responses), False

# Initialize database and LLM
db = Database()
llm = LLMIntegration()

# Conversation states
(
    REGISTER_NAME, REGISTER_ROLE, PROFILE_AGE, PROFILE_GENDER, PROFILE_CONTACTS,
    PROFILE_ACADEMIC, PROFILE_PROFESSIONALS, PROFILE_INTERESTS, PROFILE_TRIGGERS,
    PROFILE_COMMUNICATION, GROUP_NAME, GROUP_THEME, GROUP_DESC, GROUP_MAX,
    ACTIVITY_GROUP, ACTIVITY_TYPE, ACTIVITY_TITLE, ACTIVITY_DESC, ACTIVITY_DURATION
) = range(19)

# Global variables
group_message_timestamps = {}  # Track last AI intervention in groups
private_chat_sessions = {}  # Track active support sessions

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start command handler. Initiates the registration process.
    """
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    
    user = db.get_user(user_id)
    
    if user:
        await update.message.reply_text(
            f"Olá novamente, {user['name']}! Você já está registrado como {user['role']}.\n\n"
            f"Use /grupos para ver grupos disponíveis ou /atividades para ver atividades programadas."
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Olá! Bem-vindo ao AutiConnect, um espaço seguro para interação entre pessoas autistas "
        "com mediação de IA disponível 24/7.\n\n"
        "Para começar, por favor me diga seu nome:"
    )
    return REGISTER_NAME

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's name input and ask for role.
    """
    context.user_data['name'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("Pessoa Autista", callback_data='autista')],
        [InlineKeyboardButton("Auxiliar Terapêutico (AT)", callback_data='at')]
    ]
    
    await update.message.reply_text(
        f"Obrigado, {context.user_data['name']}! Qual é o seu papel?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return REGISTER_ROLE

async def process_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's role selection and complete basic registration.
    """
    query = update.callback_query
    await query.answer()
    
    role = query.data
    context.user_data['role'] = role
    
    user_id = update.effective_user.id
    name = context.user_data['name']
    
    # Create user in database
    success = db.create_user(user_id, name, role)
    
    if success:
        if role == 'autista':
            await query.edit_message_text(
                f"Registro básico concluído! Agora vamos criar seu perfil completo.\n\n"
                f"Por favor, digite sua idade:"
            )
            return PROFILE_AGE
        else:
            await query.edit_message_text(
                f"Registro concluído como Auxiliar Terapêutico (AT)!\n\n"
                f"Você pode:\n"
                f"• Criar grupos temáticos com /criar_grupo\n"
                f"• Iniciar atividades estruturadas com /iniciar_atividade\n"
                f"• Ver grupos existentes com /grupos\n"
                f"• Ver atividades programadas com /atividades"
            )
            return ConversationHandler.END
    else:
        await query.edit_message_text(
            "Desculpe, ocorreu um erro ao registrar seu usuário. Por favor, tente novamente com /start."
        )
        return ConversationHandler.END

async def process_profile_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's age input and ask for gender.
    """
    try:
        age = int(update.message.text)
        if age < 5 or age > 100:
            await update.message.reply_text(
                "Por favor, digite uma idade válida entre 5 e 100 anos."
            )
            return PROFILE_AGE
    except ValueError:
        await update.message.reply_text(
            "Por favor, digite apenas números para sua idade."
        )
        return PROFILE_AGE
    
    # Store in context for later database update
    context.user_data['profile_age'] = age
    
    # Ask for gender
    keyboard = [
        [InlineKeyboardButton("Masculino", callback_data='masculino')],
        [InlineKeyboardButton("Feminino", callback_data='feminino')],
        [InlineKeyboardButton("Não-binário", callback_data='nao-binario')],
        [InlineKeyboardButton("Prefiro não informar", callback_data='nao-informado')]
    ]
    
    await update.message.reply_text(
        "Obrigado! Qual é o seu gênero?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROFILE_GENDER

async def process_profile_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's gender selection and ask for emergency contacts.
    """
    query = update.callback_query
    await query.answer()
    
    gender = query.data
    context.user_data['profile_gender'] = gender
    
    await query.edit_message_text(
        "Obrigado! Agora, por favor, forneça contatos de emergência (pais, responsáveis ou cuidadores).\n\n"
        "Digite no formato: Nome - Relação - Telefone\n"
        "Exemplo: Maria Silva - Mãe - (11) 98765-4321\n\n"
        "Você pode adicionar múltiplos contatos, um por linha."
    )
    return PROFILE_CONTACTS

async def process_profile_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's emergency contacts and ask for academic history.
    """
    contacts_text = update.message.text
    contacts = [contact.strip() for contact in contacts_text.split('\n') if contact.strip()]
    context.user_data['profile_contacts'] = contacts
    
    await update.message.reply_text(
        "Obrigado! Agora, conte-nos brevemente sobre seu histórico acadêmico.\n"
        "Por exemplo: escolas que frequentou, nível de escolaridade, etc."
    )
    return PROFILE_ACADEMIC

async def process_profile_academic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's academic history and ask for professionals.
    """
    academic_history = update.message.text
    context.user_data['profile_academic'] = academic_history
    
    await update.message.reply_text(
        "Obrigado! Agora, por favor, liste os profissionais com quem você já trabalhou "
        "ou trabalha atualmente (terapeutas, psicólogos, etc.).\n\n"
        "Digite no formato: Nome - Especialidade\n"
        "Exemplo: Dr. João - Psicólogo\n\n"
        "Você pode adicionar múltiplos profissionais, um por linha."
    )
    return PROFILE_PROFESSIONALS

async def process_profile_professionals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's professionals and ask for interests.
    """
    professionals_text = update.message.text
    professionals = [prof.strip() for prof in professionals_text.split('\n') if prof.strip()]
    context.user_data['profile_professionals'] = professionals
    
    await update.message.reply_text(
        "Obrigado! Agora, conte-nos sobre seus interesses especiais, hobbies ou tópicos favoritos.\n"
        "Isso nos ajudará a sugerir grupos e atividades relevantes para você.\n\n"
        "Por favor, liste seus interesses separados por vírgulas."
    )
    return PROFILE_INTERESTS

async def process_profile_interests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's interests and ask for anxiety triggers.
    """
    interests_text = update.message.text
    interests = [interest.strip() for interest in interests_text.split(',') if interest.strip()]
    context.user_data['profile_interests'] = interests
    
    await update.message.reply_text(
        "Obrigado! Para nos ajudar a criar um ambiente confortável, "
        "poderia nos informar sobre gatilhos conhecidos de ansiedade ou desconforto?\n\n"
        "Por exemplo: barulhos altos, interrupções frequentes, certos tópicos, etc.\n"
        "Por favor, liste-os separados por vírgulas."
    )
    return PROFILE_TRIGGERS

async def process_profile_triggers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's anxiety triggers and ask for communication preferences.
    """
    triggers_text = update.message.text
    triggers = [trigger.strip() for trigger in triggers_text.split(',') if trigger.strip()]
    context.user_data['profile_triggers'] = triggers
    
    # Ask for communication preferences
    keyboard = [
        [InlineKeyboardButton("Direta e objetiva", callback_data='direta')],
        [InlineKeyboardButton("Detalhada e explicativa", callback_data='detalhada')]
    ]
    
    await update.message.reply_text(
        "Quase terminando! Como você prefere que nos comuniquemos com você?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PROFILE_COMMUNICATION

async def process_profile_communication(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process user's communication preferences and complete profile setup.
    """
    query = update.callback_query
    await query.answer()
    
    comm_style = query.data
    context.user_data['profile_communication'] = comm_style
    
    user_id = update.effective_user.id
    
    # Update user profile in database
    profile_data = {
        "age": context.user_data.get('profile_age'),
        "gender": context.user_data.get('profile_gender'),
        "emergency_contacts": context.user_data.get('profile_contacts', []),
        "academic_history": context.user_data.get('profile_academic', ''),
        "professionals": context.user_data.get('profile_professionals', []),
        "interests": context.user_data.get('profile_interests', []),
        "anxiety_triggers": context.user_data.get('profile_triggers', []),
        "communication_preferences": {
            "style": context.user_data.get('profile_communication', 'direta')
        }
    }
    
    success = db.update_user_profile(user_id, profile_data)
    
    if success:
        await query.edit_message_text(
            f"Perfil completo criado com sucesso!\n\n"
            f"Agora você pode:\n"
            f"• Ver grupos disponíveis com /grupos\n"
            f"• Ver atividades programadas com /atividades\n\n"
            f"Nossos agentes de IA estão disponíveis 24/7 para ajudar nas interações "
            f"e oferecer suporte quando necessário. Se precisar de ajuda individual, "
            f"você pode iniciar uma conversa privada a qualquer momento."
        )
    else:
        await query.edit_message_text(
            "Desculpe, ocorreu um erro ao salvar seu perfil completo. "
            "No entanto, seu perfil básico foi criado e você pode começar a usar o bot. "
            "Você pode atualizar seu perfil mais tarde com o comando /perfil."
        )
    
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display help information.
    """
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text(
            "Você precisa se registrar primeiro. Use /start para criar seu perfil."
        )
        return
    
    help_text = (
        "🤖 *AutiConnect Bot - Comandos Disponíveis:*\n\n"
        "/start - Iniciar ou reiniciar o bot\n"
        "/ajuda - Mostrar esta mensagem de ajuda\n"
        "/grupos - Ver grupos temáticos disponíveis\n"
        "/atividades - Ver atividades programadas\n"
        "/perfil - Atualizar seu perfil\n\n"
    )
    
    if user.get('role') == 'at':
        help_text += (
            "*Comandos exclusivos para ATs:*\n"
            "/criar_grupo - Criar um novo grupo temático\n"
            "/iniciar_atividade - Iniciar uma nova atividade estruturada\n\n"
        )
    
    help_text += (
        "O AutiConnect oferece mediadores de IA disponíveis 24/7 para facilitar interações "
        "e oferecer suporte quando necessário. Os mediadores podem ajudar com:\n\n"
        "• Facilitação de conversas em grupo\n"
        "• Suporte individual em conversas privadas\n"
        "• Estruturação de atividades\n"
        "• Detecção de situações que requerem intervenção profissional\n\n"
        "Para conversar com um mediador de IA em privado, basta enviar uma mensagem diretamente para este bot."
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    List all available thematic groups.
    """
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    
    groups = db.get_all_groups()
    
    if not groups:
        await update.message.reply_text(
            "Não há grupos disponíveis no momento.\n\n"
            "Se você é um AT, pode criar um novo grupo com /criar_grupo."
        )
        return
    
    message = "📋 *Grupos Disponíveis:*\n\n"
    
    for group in groups:
        members_count = len(group.get('members', []))
        max_members = group.get('max_members', 10)
        
        # Get AT name
        at_id = group.get('created_by')
        at = db.get_user(at_id)
        at_name = at.get('name', 'Desconhecido') if at else 'Desconhecido'
        
        # Check if AI mediator is enabled
        ai_enabled = group.get('ai_mediator_enabled', False)
        ai_status = "✅ Ativo" if ai_enabled else "❌ Inativo"
        
        message += (
            f"*{group['name']}*\n"
            f"📝 Tema: {group['theme']}\n"
            f"👥 Membros: {members_count}/{max_members}\n"
            f"👨‍⚕️ AT: {at_name}\n"
            f"🤖 Mediador IA: {ai_status}\n"
            f"ℹ️ {group['description']}\n\n"
        )
    
    # Add join button
    keyboard = []
    for group in groups:
        if len(group.get('members', [])) < group.get('max_members', 10):
            keyboard.append([InlineKeyboardButton(
                f"Entrar: {group['name']}", 
                callback_data=f"join_{group['group_id']}"
            )])
    
    if keyboard:
        await update.message.reply_text(
            message, 
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def join_group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle group join button callback.
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    group_id = int(query.data.split('_')[1])
    
    # Add user to group
    success = db.add_user_to_group(user_id, group_id)
    
    if success:
        group = db.get_group(group_id)
        group_name = group.get('name', 'Grupo') if group else 'Grupo'
        
        await query.edit_message_text(
            f"Você entrou no grupo '{group_name}' com sucesso!\n\n"
            f"Em uma implementação completa, você seria adicionado ao grupo do Telegram. "
            f"Para este MVP, considere-se membro do grupo e use /atividades para "
            f"ver as atividades programadas."
        )
    else:
        await query.edit_message_text(
            "Desculpe, ocorreu um erro ao entrar no grupo. Por favor, tente novamente."
        )

async def create_group_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the group creation process (AT only).
    """
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text(
            "Você precisa se registrar primeiro. Use /start para criar seu perfil."
        )
        return ConversationHandler.END
    
    if user.get('role') != 'at':
        await update.message.reply_text(
            "Desculpe, apenas Auxiliares Terapêuticos (ATs) podem criar grupos."
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Vamos criar um novo grupo temático.\n\n"
        "Qual será o nome do grupo?"
    )
    return GROUP_NAME

async def process_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process group name input and ask for theme.
    """
    context.user_data['group_name'] = update.message.text
    
    await update.message.reply_text(
        f"Ótimo! O nome do grupo será: {context.user_data['group_name']}\n\n"
        f"Agora, qual será o tema principal deste grupo? (ex: videogames, música, ciência)"
    )
    return GROUP_THEME

async def process_group_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process group theme input and ask for description.
    """
    context.user_data['group_theme'] = update.message.text
    
    await update.message.reply_text(
        f"Tema definido: {context.user_data['group_theme']}\n\n"
        f"Por favor, forneça uma breve descrição do propósito deste grupo:"
    )
    return GROUP_DESC

async def process_group_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process group description input and ask for max members.
    """
    context.user_data['group_desc'] = update.message.text
    
    await update.message.reply_text(
        f"Descrição registrada. Qual será o número máximo de participantes? (recomendado: 8-12)"
    )
    return GROUP_MAX

async def process_group_max(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process max members input and create the group.
    """
    try:
        max_members = int(update.message.text)
        if max_members < 2 or max_members > 50:
            await update.message.reply_text(
                "Por favor, escolha um número entre 2 e 50. Qual será o número máximo de participantes?"
            )
            return GROUP_MAX
    except ValueError:
        await update.message.reply_text(
            "Por favor, digite apenas números. Qual será o número máximo de participantes?"
        )
        return GROUP_MAX
    
    context.user_data['group_max'] = max_members
    
    # Create a temporary group ID (in a real implementation, this would be the actual Telegram group ID)
    # For this MVP, we'll use a timestamp-based ID
    group_id = int(datetime.now().timestamp())
    
    user_id = update.effective_user.id
    
    # Create group in database
    success = db.create_group(
        group_id=group_id,
        name=context.user_data['group_name'],
        theme=context.user_data['group_theme'],
        description=context.user_data['group_desc'],
        created_by=user_id,
        max_members=context.user_data['group_max']
    )
    
    if success:
        await update.message.reply_text(
            f"✅ Grupo '{context.user_data['group_name']}' criado com sucesso!\n\n"
            f"Em uma implementação completa, você receberia um link para convidar participantes. "
            f"Para este MVP, considere o grupo criado e pronto para uso.\n\n"
            f"Use /iniciar_atividade para começar uma atividade neste grupo."
        )
    else:
        await update.message.reply_text(
            "Desculpe, ocorreu um erro ao criar o grupo. Por favor, tente novamente."
        )
    
    return ConversationHandler.END

async def list_activities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    List upcoming activities for the user's groups.
    """
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    
    activities = db.get_user_activities(user_id)
    
    if not activities:
        await update.message.reply_text(
            "Não há atividades programadas para seus grupos no momento.\n\n"
            "Se você é um AT, pode iniciar uma nova atividade com /iniciar_atividade."
        )
        return
    
    message = "📅 *Atividades Programadas:*\n\n"
    
    for activity in activities:
        # Get group name
        group_id = activity.get('group_id')
        group = db.get_group(group_id)
        group_name = group.get('name', 'Desconhecido') if group else 'Desconhecido'
        
        # Format scheduled time
        scheduled_time = activity.get('scheduled_time', 'Não definido')
        if scheduled_time != 'Não definido':
            if isinstance(scheduled_time, datetime):
                scheduled_time = scheduled_time.strftime("%d/%m/%Y às %H:%M")
        
        # Check if AI guidance is enabled
        ai_enabled = activity.get('ai_guidance_enabled', False)
        ai_status = "✅ Ativo" if ai_enabled else "❌ Inativo"
        
        message += (
            f"*{activity['title']}*\n"
            f"📝 Tipo: {activity['type']}\n"
            f"👥 Grupo: {group_name}\n"
            f"🕒 Quando: {scheduled_time}\n"
            f"⏱️ Duração: {activity.get('duration', 60)} minutos\n"
            f"🤖 Guia IA: {ai_status}\n"
            f"ℹ️ {activity['description']}\n\n"
        )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def start_activity_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the activity creation process (AT only).
    """
    user_id = update.effective_user.id
    db.update_last_active(user_id)
    
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text(
            "Você precisa se registrar primeiro. Use /start para criar seu perfil."
        )
        return ConversationHandler.END
    
    if user.get('role') != 'at':
        await update.message.reply_text(
            "Desculpe, apenas Auxiliares Terapêuticos (ATs) podem iniciar atividades."
        )
        return ConversationHandler.END
    
    # Get groups where user is AT
    groups = db.get_all_groups()
    at_groups = [g for g in groups if g.get('created_by') == user_id]
    
    if not at_groups:
        await update.message.reply_text(
            "Você não tem nenhum grupo como AT. Crie um grupo primeiro com /criar_grupo."
        )
        return ConversationHandler.END
    
    # Store groups in context for later use
    context.user_data['at_groups'] = at_groups
    
    # Create keyboard with group options
    keyboard = []
    for group in at_groups:
        keyboard.append([InlineKeyboardButton(group['name'], callback_data=f"group_{group['group_id']}")])
    
    await update.message.reply_text(
        "Vamos iniciar uma nova atividade estruturada.\n\n"
        "Primeiro, selecione o grupo para esta atividade:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ACTIVITY_GROUP

async def process_activity_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process group selection for activity and ask for activity type.
    """
    query = update.callback_query
    await query.answer()
    
    group_id = int(query.data.split('_')[1])
    context.user_data['activity_group_id'] = group_id
    
    # Find group name
    group_name = next((g['name'] for g in context.user_data['at_groups'] if g['group_id'] == group_id), "Grupo")
    context.user_data['activity_group_name'] = group_name
    
    # Activity type options
    keyboard = [
        [InlineKeyboardButton("Discussão Temática", callback_data="type_discussao")],
        [InlineKeyboardButton("Projeto Colaborativo", callback_data="type_projeto")],
        [InlineKeyboardButton("Jogo Social", callback_data="type_jogo")],
        [InlineKeyboardButton("Compartilhamento de Interesses", callback_data="type_compartilhamento")]
    ]
    
    await query.edit_message_text(
        f"Grupo selecionado: {group_name}\n\n"
        f"Qual tipo de atividade você deseja iniciar?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ACTIVITY_TYPE

async def process_activity_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process activity type selection and ask for title.
    """
    query = update.callback_query
    await query.answer()
    
    activity_type = query.data.split('_')[1]
    context.user_data['activity_type'] = activity_type
    
    # Map type codes to readable names
    type_names = {
        'discussao': 'Discussão Temática',
        'projeto': 'Projeto Colaborativo',
        'jogo': 'Jogo Social',
        'compartilhamento': 'Compartilhamento de Interesses'
    }
    
    context.user_data['activity_type_name'] = type_names.get(activity_type, activity_type)
    
    await query.edit_message_text(
        f"Tipo de atividade: {context.user_data['activity_type_name']}\n\n"
        f"Qual será o título desta atividade?"
    )
    
    return ACTIVITY_TITLE

async def process_activity_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process activity title input and ask for description.
    """
    context.user_data['activity_title'] = update.message.text
    
    await update.message.reply_text(
        f"Título: {context.user_data['activity_title']}\n\n"
        f"Por favor, forneça uma breve descrição desta atividade:"
    )
    
    return ACTIVITY_DESC

async def process_activity_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process activity description input and ask for duration.
    """
    context.user_data['activity_desc'] = update.message.text
    
    await update.message.reply_text(
        f"Descrição registrada. Qual será a duração desta atividade em minutos? (ex: 30, 60)"
    )
    
    return ACTIVITY_DURATION

async def process_activity_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Process activity duration input and create the activity.
    """
    try:
        duration = int(update.message.text)
        if duration < 5 or duration > 180:
            await update.message.reply_text(
                "Por favor, escolha uma duração entre 5 e 180 minutos."
            )
            return ACTIVITY_DURATION
    except ValueError:
        await update.message.reply_text(
            "Por favor, digite apenas números para a duração em minutos."
        )
        return ACTIVITY_DURATION
    
    context.user_data['activity_duration'] = duration
    
    user_id = update.effective_user.id
    
    # Create activity in database
    activity_id = db.create_activity(
        group_id=context.user_data['activity_group_id'],
        activity_type=context.user_data['activity_type'],
        title=context.user_data['activity_title'],
        description=context.user_data['activity_desc'],
        created_by=user_id,
        duration=context.user_data['activity_duration']
    )
    
    if activity_id:
        await update.message.reply_text(
            f"✅ Atividade '{context.user_data['activity_title']}' criada com sucesso para o grupo "
            f"'{context.user_data['activity_group_name']}'!\n\n"
            f"Em uma implementação completa, todos os membros do grupo seriam notificados. "
            f"Para este MVP, considere a atividade criada e pronta para começar.\n\n"
            f"Use /atividades para ver todas as atividades programadas."
        )
    else:
        await update.message.reply_text(
            "Desculpe, ocorreu um erro ao criar a atividade. Por favor, tente novamente."
        )
    
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages with AI mediation.
    """
    message = update.message
    user_id = message.from_user.id
    text = message.text
    
    # Get user from database
    user = db.get_user(user_id)
    
    # If user doesn't exist, suggest registration
    if not user:
        await message.reply_text(
            "Olá! Parece que você ainda não está registrado. Use /start para criar seu perfil."
        )
        return
    
    # Check if this is a private chat or group chat
    if message.chat.type == 'private':
        # Generate AI support response
        ai_response, alert_needed = llm.provide_individual_support(user_id, text)
        
        if ai_response:
            await message.reply_text(
                f"🤖 *Assistente IA*: {ai_response}",
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        # For group chats, this would handle AI mediation
        # In this MVP, we'll just acknowledge the message
        pass

def main() -> None:
    """Start the bot."""
    # Get the token from environment variable
    token = os.environ.get('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN environment variable not set")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add conversation handler for registration and profile creation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)],
            REGISTER_ROLE: [CallbackQueryHandler(process_role)],
            PROFILE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_age)],
            PROFILE_GENDER: [CallbackQueryHandler(process_profile_gender)],
            PROFILE_CONTACTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_contacts)],
            PROFILE_ACADEMIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_academic)],
            PROFILE_PROFESSIONALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_professionals)],
            PROFILE_INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_interests)],
            PROFILE_TRIGGERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_profile_triggers)],
            PROFILE_COMMUNICATION: [CallbackQueryHandler(process_profile_communication)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(conv_handler)
    
    # Add conversation handler for group creation
    group_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('criar_grupo', create_group_start)],
        states={
            GROUP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_name)],
            GROUP_THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_theme)],
            GROUP_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_desc)],
            GROUP_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_group_max)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(group_conv_handler)
    
    # Add conversation handler for activity creation
    activity_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('iniciar_atividade', start_activity_command)],
        states={
            ACTIVITY_GROUP: [CallbackQueryHandler(process_activity_group, pattern=r'^group_')],
            ACTIVITY_TYPE: [CallbackQueryHandler(process_activity_type, pattern=r'^type_')],
            ACTIVITY_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_activity_title)],
            ACTIVITY_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_activity_desc)],
            ACTIVITY_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_activity_duration)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(activity_conv_handler)
    
    # Add other command handlers
    application.add_handler(CommandHandler('ajuda', help_command))
    application.add_handler(CommandHandler('grupos', list_groups))
    application.add_handler(CommandHandler('atividades', list_activities))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(join_group_callback, pattern=r'^join_'))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
