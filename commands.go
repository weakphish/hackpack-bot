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
		"ping": pingCommand,
		// 'ctf' command group. The function is defined below for cleanliness
		"ctf": ctfCommand,
	}
)

// Ping command handler
func pingCommand(s *discordgo.Session, i *discordgo.InteractionCreate) {
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Pong!",
		},
	})
}

// This function handles the response action(s) for the 'ctf' group of ApplicationCommands
func ctfCommand(s *discordgo.Session, i *discordgo.InteractionCreate) {
	var respContent string = "Response Content"
	var ctfName string
	var respComponents []discordgo.MessageComponent
	data := i.ApplicationCommandData()

	// Check which subcommand was called
	switch data.Options[0].Name {
	case "create":
		ctfName = data.Options[0].Options[0].StringValue()
		log.Printf("New CTF Name given: %s\n", ctfName)

		/*
			// Create the new role for the CTF
			newRole, err := s.GuildRoleCreate(GlobalConfig.GuildID)
			if err != nil {
				content = "Could not create new guild role: " + err.Error()
			} else {
				s.GuildRoleEdit(GlobalConfig.GuildID, newRole.ID, ctfName, 0, false, 0, true)
				content = "Created CTF role " + ctfName
			}
		*/

		// Reply with a button to allow quickly joining the CTF
		actionRow := discordgo.ActionsRow{
			Components: []discordgo.MessageComponent{
				discordgo.Button{
					Label:    "Join CTF!",
					Style:    discordgo.SuccessButton,
					Disabled: false,
					CustomID: "joined_ctf",
				},
			},
		}
		respComponents = append(respComponents, actionRow)
	}

	// Send back the status reply
	err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content:    respContent,
			Components: respComponents,
		},
	})
	if err != nil {
		log.Print(err)
	}
}
