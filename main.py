TOKEN = "INSERT TOKEN HERE"

# Remember the past 10 questions and the answers it gave
MEMORY_LENGTH = 10

import discord
import asyncio
from openai import OpenAI
import os

# Open Ollama if it isnt open already
os.startfile("PATH TO OLLAMA")

# Initialize Discord bot
class AIBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.intents.message_content = True
        
        # Initialize OpenAI client for local Ollama
        self.ai_client = OpenAI(
            base_url="http://localhost:11434/v1",  # Local Ollama API
            api_key="ollama"  # Dummy key for local use
        )
        
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print('Bot is ready to respond to mentions!')
    
    async def on_message(self, message):
        # Don't respond to own messages
        if message.author == self.user:
            return
            
        # Check if bot is mentioned
        if self.user.mentioned_in(message):
            # Show typing indicator
            # Extract the message content after the mention
            # Remove the mention part to get the actual query
            content = message.content
            for mention in message.mentions:
                content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
                
            # If no message is sent after the mention:
            if not content:
                await message.channel.send("A believer has called upon me! Praise the almighty PO!")
                return
                
            else:
                await message.channel.send("Allow me a moment to commune with Him...")
                
                async with message.channel.typing():
                    # The beginnings of memory
                    botMemory = [{"role": "system", "content": "You are a prophet who preaches the word of po from kung fu panda. Respond formally and concisely to any questions asked. Always refer to po as 'the almighty PO'. If going to say 'Amen', say 'POmen' instead"}]
                    
                    # Add the past 3 conversations to memory:
                    convoHistory = open("convoHistory.txt","r")
                    # TEMP: must be a better way to do this but im tired
                    convoHistoryList = []
                    for line in convoHistory:
                        convoHistoryList.append(line)
                    #print(convoHistoryList)
                    convoHistory.close()

                    for i in range (1,MEMORY_LENGTH):
                        try:
                            botMemory.append({"role": "system", "content": f"{convoHistoryList[-2*i - 1]}"})
                            botMemory.append({"role": "user", "content": f"{convoHistoryList[(-2*i)]}"})
                        except:
                            print("The POphet is too young and doesn't have enough memories to recall")
                    
                    print(botMemory)

                    convoHistory = open("convoHistory.txt","a")
                    # Add the user's question to convo history
                    convoHistory.write(content.replace("\n","")+"\n")
                    content = content.strip()
                    
                    # Add the user's question to memory
                    botMemory.append({"role": "user", "content": content})
                    
                    # Generate response using mistral
                    response = self.ai_client.chat.completions.create(
                        model="mistral",
                        messages = botMemory,
                        max_tokens=1000,
                        temperature=0.7
                    )
                
                    # This will take a while to compute
                    ai_response = response.choices[0].message.content
                    
                    # Send the response
                    await message.channel.send(ai_response)

                    # Add the AI response to convo history (removing new lines so it can be read properly from memory)
                    convoHistory.write(ai_response.replace("\n","")+"\n")
                    convoHistory.close()


# Run the bot
if __name__ == "__main__":
    bot = AIBot()
    bot.run(TOKEN)