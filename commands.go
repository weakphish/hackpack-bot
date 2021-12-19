package main

import (
	"log"

	"github.com/bwmarrin/discordgo"
)

// Define our ApplicationCommands
var (
	// Create an array of ApplicationCommand structs to register the definitions of our commands
	commands = []*discordgo.ApplicationCommand{
		{
			Name:        "ping",
			Description: "ping-command",
		},
		{
			Name:        "ctf",
			Type:        discordgo.ChatApplicationCommand,
			Description: "Parent command for the CTF group",
			// Subcommands for 'ctf'
			Options: []*discordgo.ApplicationCommandOption{
				{
					Name:        "create",
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Description: "Create a CTF",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "ctf-name",
							Description: "CTF name",
							Required:    true,
						},
					},
				},
				{
					Name:        "join",
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Description: "Join a CTF",
				},
			},
		},
	}

	// Create a map of <CommandName>:<HandlerFunction> for each command. Each command will
	// correspond to a first-class function that will handle the command's usage upon invocation
	commandHandlers = map[string]func(s *discordgo.Session, i *discordgo.InteractionCreate){
		// Ping command
		"ping": func(s *discordgo.Session, i *discordgo.InteractionCreate) {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Content: "Hey there! Congratulations, you just executed your first slash command",
				},
			})
		},
		// 'ctf' command group. The function is defined below for cleanliness
		"ctf": ctfCommand,
	}
)

// Handler function for the 'ctf' group of commands
func ctfCommand(s *discordgo.Session, i *discordgo.InteractionCreate) {
	var content string
	var ctfName string
	data := i.ApplicationCommandData()

	switch data.Options[0].Name {
	case "create":
		// Ensure an argument was provided before we go indexing arrays
		if len(data.Options[0].Options) > 0 {
			ctfName = data.Options[0].Options[0].StringValue()
			log.Printf("CTF Name given: %s\n", ctfName)

			// Create the new role for the CTF
			newRole, err := s.GuildRoleCreate(*GuildID)
			if err != nil {
				content = "Could not creat new guild role."
			}
			newRole.Name = ctfName
		} else {
			content = "No argument provided"
		}
	}

	// Send back the reply
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: content,
		},
	})
}
