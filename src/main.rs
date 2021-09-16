use std::fs;

use serenity::client::{Context, EventHandler};
use serenity::framework::standard::{macros::group, StandardFramework};
use serenity::model::gateway::Ready;
use serenity::model::id::GuildId;
use serenity::model::interactions::application_command::{
    ApplicationCommand, ApplicationCommandOptionType,
};
use serenity::model::interactions::{Interaction, InteractionResponseType};
use serenity::{async_trait, Client};

#[group]
struct General;

/// Handler for the application - will implement an EventHandler as _part_ of this
struct Handler;

#[async_trait]
impl EventHandler for Handler {
    // From docs:
    // Dispatched upon startup.
    // Provides data about the bot and the guilds it’s in.
    async fn ready(&self, ctx: Context, _data_about_bot: Ready) {
        // Register each command name and description
        let commands = ApplicationCommand::set_global_application_commands(&ctx.http, |commands| {
            commands.create_application_command(|command| {
                command.name("ping").description("A ping command")
            })
        })
        .create_application_command(|command| {
            command
                .name("ctf-create")
                .description("Create a CTF channel.")
                .create_option(|option| {
                    option
                        .name("event-name")
                        .description("The name of the CTF event.")
                        .kind(ApplicationCommandOptionType::User)
                        .required(true)
                })
        })
        .await;

        println!(
            "I now have the following global slash commands: {:#?}",
            commands
        );
    }

    // From docs:
    // Dispatched when an interaction is created (e.g a slash command was used or a button was clicked).
    // Provides the created interaction.
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        // Figure out what interaction was sent
        if let Interaction::ApplicationCommand(command) = interaction {
            let content = match command.data.name.as_str() {
                "ping" => "Hey!".to_string(),
                _ => "I didn't get that.".to_string(),
            };

            // Create responses and shoot them off back to the channel
            if let Err(why) = command
                .create_interaction_response(&ctx.http, |response| {
                    response
                        .kind(InteractionResponseType::ChannelMessageWithSource)
                        .interaction_response_data(|message| message.content(content))
                })
                .await
            {
                println!("Cannot respond to slash command: {}", why);
            }
        }
    }
}

#[tokio::main]
async fn main() {
    // Load framework
    let framework = StandardFramework::new()
        .configure(|c| c.prefix("!"))
        .group(&GENERAL_GROUP);

    // The Application Id is usually the Bot User Id.
    let application_id: u64 = fs::read_to_string("app_id")
        .expect("Could not read file.")
        .parse()
        .expect("Something went wrong reading the file");

    // Load token into client
    let token = fs::read_to_string("secret").expect("Something went wrong reading the file");
    let mut client = Client::builder(token)
        .event_handler(Handler)
        .application_id(application_id)
        .framework(framework)
        .await
        .expect("Could not create client.");

    // Start listening on the client (single shard)
    if let Err(why) = client.start().await {
        println!("An error occurred starting the client: {:?}", why);
    }
}
