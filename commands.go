package main

import "github.com/bwmarrin/discordgo"

// Define our commands
var (
	commands = []*discordgo.ApplicationCommand{
		{
			Name:        "ping",
			Description: "ping-command",
		},
		{
			Name:        "ctf",
			Type:        discordgo.ChatApplicationCommand,
			Description: "Parent command for the CTF group",
			Options: []*discordgo.ApplicationCommandOption{
				{
					Name:        "create",
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Description: "Create a CTF",
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
	// correspond to a first-class function that will handle the command's usage.
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
		// CTF Group
		// Reference: https://github.com/bwmarrin/discordgo/blob/master/examples/slash_commands/main.go
		// Line 227
		"ctf": func(s *discordgo.Session, i *discordgo.InteractionCreate) {
			var content string

			// As you can see, the name of subcommand (nested, top-level) or subcommand group
			// is provided through arguments.
			switch i.ApplicationCommandData().Options[0].Name {
			case "create":
				content = "The top-level subcommand is executed. Now try to execute the nested one."
				ctfName := i.ApplicationCommandData().Options[1].Name
				s.GuildRoleCreate(ctfName)
			}

			// Send back the reply
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Content: content,
				},
			})
		},
	}
)
