package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
	"os/signal"

	"github.com/bwmarrin/discordgo"
)

// BotConfig
// Bot configuration that will tell it how to connect to the Discord Application.
// The bot expects a `config.json` file with the following fields:
// bot_token, guild_id, remove_commands
type BotConfig struct {
	GuildID        string `json:"guild_id"`
	BotToken       string `json:"bot_token"`
	RemoveCommands bool   `json:"remove_commands"`
}

// GlobalConfig
// Global configuration struct
var GlobalConfig BotConfig

// Session pointer for our discord session
var session *discordgo.Session

// This function runs prior to the main function. Executes some basic setup stuff.
func init() {
	// Read config file
	content, err := ioutil.ReadFile("./config.json")
	if err != nil {
		log.Fatal("Error when opening file: ", err)
	}

	err = json.Unmarshal(content, &GlobalConfig)
	if err != nil {
		log.Fatal("Error during Unmarshal(): ", err)
	}

	session, err = discordgo.New("Bot " + GlobalConfig.BotToken)
	if err != nil {
		log.Fatalf("Invalid bot parameters: %v", err)
	}

	// Add handlers for different components (commands / message components)
	session.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		switch i.Type {
		case discordgo.InteractionApplicationCommand:
			if handler, ok := commandHandlers[i.ApplicationCommandData().Name]; ok {
				handler(s, i)
			}

		case discordgo.InteractionMessageComponent:
			if h, ok := componentsHandlers[i.MessageComponentData().CustomID]; ok {
				h(s, i)
			}
		}
	})
}

func main() {
	// Print status and open up the bot session
	session.AddHandler(func(s *discordgo.Session, r *discordgo.Ready) {
		log.Println("Bot is up!")
	})
	err := session.Open()
	if err != nil {
		log.Fatalf("Cannot open the session: %v", err)
	}

	// Register each application command
	for _, v := range commands {
		_, err := session.ApplicationCommandCreate(session.State.User.ID, GlobalConfig.GuildID, v)
		if err != nil {
			log.Panicf("Cannot create '%v' command: %v", v.Name, err)
		}
	}

	// End the session gracefully
	defer session.Close()
	stop := make(chan os.Signal)
	signal.Notify(stop, os.Interrupt)
	<-stop
	log.Println("Gracefully shutting down")
}
