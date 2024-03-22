import logging
import asyncio
from aiohttp import ClientSession
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import re
import nest_asyncio

nest_asyncio.apply()

TELEGRAM_TOKEN = "YOUR TOKEN HERE"
ENTER_CONTRACT_ADDRESS = 1

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context) -> None:
    keyboard = [
        [InlineKeyboardButton("AnzenVM", callback_data='option_1')],
        [InlineKeyboardButton("AnzenAI", callback_data='anzen_ai')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '''
<b>🤖Welcome to AnzenBot🤖</b>
Here you can deploy private encrypted VMs and run AI powered smart contract audits.
Please choose an option:
    '''
    if update.callback_query:
        await update.callback_query.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'option_1':
        keyboard = [
            [InlineKeyboardButton("Try AnzenVM Beta", callback_data='anzen_vm')],
            [InlineKeyboardButton("Back to Main Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = '''
<b><u>AnzenVM provides private Virtual Machines</u></b>
🔓 Encrypted private traffic
✅ Access your server via url
🔥 No downloads and no need to for complex RDP sessions
Try our beta below:
        '''
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    elif query.data == 'anzen_vm':
        text = '''
👷Building your VM👷 
Please wait. This should take about 70 seconds...
        '''
        await query.edit_message_text(text=text)
        response = await make_http_request('https://wyz5a42qzuh7eavf4wo6bllydm0wrptz.lambda-url.us-west-2.on.aws/', {
            'username': update.effective_user.username,
            'user_id': update.effective_user.id,
            'chat_id': update.effective_chat.id
        })
        if response:
            environment_url = response.get('environment_url', 'No URL found in the response.')
            text = f'''
Please access your VM by using this link:
<a href="{environment_url}">Click here to access your VM</a>
✍️To copy + paste into and out of your VM, press Ctrl+Alt+Shift
📱 If on a mobile device, swipe from left to right and select Text Input to type
Access to your VM expires after 1 hour in our beta version
            '''
            keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
        # Existing elif block for 'anzen_vm' continues here...
    elif query.data == 'anzen_ai':
        keyboard = [
            [InlineKeyboardButton("Ethereum", callback_data='ethereum')],
            [InlineKeyboardButton("Polygon", callback_data='polygon')],
            [InlineKeyboardButton("BSC", callback_data='bsc')],
            [InlineKeyboardButton("Arbitrum", callback_data='arbitrum')],
            [InlineKeyboardButton("Back to Main Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = '''
<b><u>AnzenAI performs AI powered smart contract audits</u></b>
✅Reliable
✅Multichain
✅Fast
Choose a chain to get started:
        '''
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')
    elif query.data in ['ethereum', 'polygon', 'bsc', 'arbitrum']:
        context.user_data['chain_selection'] = query.data
        text = f"You have selected {query.data}. Please enter the smart contract address you would like audited:"
        await query.edit_message_text(text=text)
        return ENTER_CONTRACT_ADDRESS
    elif query.data == 'back':
        await start(update, context)

# This script has been Modified by Nilufa Begum

async def handle_text_input(update: Update, context) -> None:
    if 'chain_selection' in context.user_data:
        contract_address = update.message.text
        # Prepare the data for the HTTP request
        data = {
            'contract_address': contract_address,
            'chain_selection': context.user_data['chain_selection']
        }
        response = await make_http_request('https://j27syjuatgape4pxsrnknttmwq0fgocn.lambda-url.us-west-2.on.aws/', data)
        if response:
            ai_response = response.get('ai_response', 'No response found.')
            cleaned_ai_response = re.sub(r'\#{2,}', '', ai_response)
            cleaned_ai_response = re.sub(r'\*{2,}', '', cleaned_ai_response)
            text = cleaned_ai_response
            keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text=text, reply_markup=reply_markup)
        else:
            await update.message.reply_text("An error occurred. Please try again.")
        context.user_data.clear()

# Register handle_text_input in the main function:
async def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.text & ~filters.command, handle_text_input))
    application.add_error_handler(error)
    await application.run_polling()


async def make_http_request(url, data):
    async with ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"HTTP request failed with status code {response.status}")
                return None

async def error(update: Update, context) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

async def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error)
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
