package main

import (
	"log"

	"github.com/bwmarrin/discordgo"
)

// ID for the CTF text channel category
const ctfCategoryID = "1259233177994661910"

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
					Name:        "leave",
					Type:        discordgo.ApplicationCommandOptionSubCommand,
					Description: "Leave a CTF",
					Options: []*discordgo.ApplicationCommandOption{
						{
							Type:        discordgo.ApplicationCommandOptionString,
							Name:        "ctf-name",
							Description: "CTF name",
							Required:    false,
						},
					},
				},
			},
		},
	}

	// Create a map of <CommandName>:<HandlerFunction> for each command. Each command will
	// correspond to a first-class function that will handle the command's usage upon invocation
	// commandHandlers = map[string]func(s *discordgo.Session, i *discordgo.InteractionCreate){
		// Ping command
		// "ping": pingCommandCallback,
		// 'ctf' command group. The function is defined below for cleanliness
		// "ctf": ctfCommandCallback,
	// }

	// Define handlers for message components. That is to say, what will be executed when a
	// component is interacted with.
	// componentsHandlers = map[string]func(s *discordgo.Session, i *discordgo.InteractionCreate){
	// 	"ctf_join":  joinCTF,
	//	"ctf_leave": leaveCTF,
	// }
)

// Ping command handler
func pingCommandCallback(s *discordgo.Session, i *discordgo.InteractionCreate) {
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Pong!",
		},
	})
}

// This function handles the response action(s) for the 'ctf' group of ApplicationCommands
func ctfCommandCallback(s *discordgo.Session, i *discordgo.InteractionCreate) {
	var respContent string
	var ctfName string
	var respComponents []discordgo.MessageComponent
	var leaveRespComponent []discordgo.MessageComponent

	data := i.ApplicationCommandData()

	// Check which subcommand was called
	switch data.Options[0].Name {
	case "create":
		ctfName = data.Options[0].Options[0].StringValue()
		log.Printf("New CTF Name given: %s\n", ctfName)

		// Create the new role for the CTF
		roleParams := &discordgo.RoleParams{
			Name: ctfName,
		}
		newRole, err := s.GuildRoleCreate(GlobalConfig.GuildID, roleParams)
		if err != nil {
			respContent = "Could not create new guild role: " + err.Error()
		} else {
			respContent = ctfName
		}

		// Reply with a button to allow quickly joining the CTF
		actionRow := discordgo.ActionsRow{
			Components: []discordgo.MessageComponent{
				discordgo.Button{
					Label:    "Join " + ctfName,
					Style:    discordgo.SuccessButton,
					Disabled: false,
					CustomID: "ctf_join",
				},
			},
		}
		respComponents = append(respComponents, actionRow)

		leaveActionRow := discordgo.ActionsRow{
			Components: []discordgo.MessageComponent{
				discordgo.Button{
					Label:    "Leave " + ctfName,
					Style:    discordgo.SuccessButton,
					Disabled: false,
					CustomID: "ctf_leave",
				},
			},
		}
		leaveRespComponent = append(leaveRespComponent, leaveActionRow)

		// Create a channel for the CTF that is locked to the created role
		targetGuild, _ := s.Guild(i.GuildID)
		everyoneID := targetGuild.Roles[0].ID // Per my assumption, @everyone is the first role - Jack

		channel, err := s.GuildChannelCreateComplex(i.GuildID, discordgo.GuildChannelCreateData{
			Name:     ctfName,
			Type:     discordgo.ChannelTypeGuildText,
			Topic:    "Channel for " + ctfName,
			ParentID: ctfCategoryID,
			PermissionOverwrites: []*discordgo.PermissionOverwrite{
				{ // deny everyone read perms
					ID:    everyoneID,
					Type:  0,
					Deny:  discordgo.PermissionViewChannel,
					Allow: 0,
				},
				{ // allow the new role to view and send messages
					ID:    newRole.ID,
					Type:  0,
					Deny:  0,
					Allow: discordgo.PermissionViewChannel | discordgo.PermissionSendMessages,
				},
			},
		})

		log.Println(channel)

		if err != nil {
			s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
				Type: discordgo.InteractionResponseChannelMessageWithSource,
				Data: &discordgo.InteractionResponseData{
					Flags:   1 << 6,
					Content: "Could not create channel",
				},
			})
		} else {
			log.Println(err)
		}

		s.ChannelMessageSendComplex(channel.ID, &discordgo.MessageSend{
			Content:    ctfName,
			Components: leaveRespComponent,
		})
	case "join":
		if len(data.Options) > 0 && len(data.Options[0].Options) > 0 {
			ctfName := data.Options[0].Options[0].StringValue()
			joinCTFCallback(s, i, ctfName)
			// We respond in the function call, no need to attempt to respond twice.
			return
		}

	case "leave":
		if len(data.Options) > 0 && len(data.Options[0].Options) > 0 {
			ctfName := data.Options[0].Options[0].StringValue()
			leaveCTFCallback(s, i, ctfName)
			// We respond in the function call, no need to attempt to respond twice.
			return
		}
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

func joinCTF(s *discordgo.Session, i *discordgo.InteractionCreate) {

	ctfName := i.Message.Content
	joinCTFCallback(s, i, ctfName)
}

func leaveCTF(s *discordgo.Session, i *discordgo.InteractionCreate) {
	ctfName := i.Message.Content
	leaveCTFCallback(s, i, ctfName)
}

func joinCTFCallback(s *discordgo.Session, i *discordgo.InteractionCreate, ctfName string) {
	guild, err := s.Guild(i.GuildID)
	if err != nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Flags:   1 << 6,
				Content: "Couldn't find the calling Guild",
			},
		})

		log.Println(err)
		return
	}

	callingUser := i.Member.User
	log.Printf("Adding user %s to CTF %s", callingUser.Username, ctfName)
	var targetRole *discordgo.Role
	for _, role := range guild.Roles {
		if role.Name == ctfName {
			targetRole = role
			break
		}
	}

	if targetRole == nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Flags:   1 << 6,
				Content: "Could not find role: " + ctfName,
			},
		})

		log.Println(err)
		return
	}

	// Add the user to the role
	err = s.GuildMemberRoleAdd(i.GuildID, callingUser.ID, targetRole.ID)
	if err != nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Flags:   1 << 6,
				Content: "Could not add role to caller",
			},
		})

		log.Println(err)
		return
	}

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Added you to " + targetRole.Name,
		},
	})
}

func leaveCTFCallback(s *discordgo.Session, i *discordgo.InteractionCreate, ctfName string) {
	guild, err := s.Guild(i.GuildID)
	if err != nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Flags:   1 << 6,
				Content: "Couldn't find the calling Guild",
			},
		})

		log.Println(err)
		return
	}

	callingUser := i.Member.User
	log.Printf("Removing user %s from CTF %s", callingUser.Username, ctfName)
	var targetRole *discordgo.Role
	for _, role := range guild.Roles {
		if role.Name == ctfName {
			targetRole = role
			break
		}
	}

	if targetRole == nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Flags:   1 << 6,
				Content: "Could not find role: " + ctfName,
			},
		})

		log.Println(err)
		return
	}

	// Remove the user from the role
	err = s.GuildMemberRoleRemove(i.GuildID, callingUser.ID, targetRole.ID)
	if err != nil {
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Flags:   1 << 6,
				Content: "Could not remove role from caller",
			},
		})

		log.Println(err)
		return
	}

	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Content: "Removed you from " + targetRole.Name,
		},
	})
}

