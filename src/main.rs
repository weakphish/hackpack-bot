mod annoyance;
mod verification;

use annoyance::AnnoyanceApplicationCommand;
use verification::EmailVerificationApplicationCommand;

use serenity::client::{Context, EventHandler};
use serenity::model::interactions::application_command::ApplicationCommandInteraction;
use serenity::model::{
    guild::Guild,
    interactions::{application_command::ApplicationCommand, Interaction},
};

use serenity::{async_trait, Client};

use std::env;
use std::error::Error;

const APPLICATION_COMMANDS: &[&(dyn ApplicationCommandHandler + Sync)] = &[
    &EmailVerificationApplicationCommand,
    &AnnoyanceApplicationCommand,
];

#[async_trait]
trait ApplicationCommandHandler {
    async fn register_command(
        &self,
        ctx: Context,
        guild: &Guild,
    ) -> Result<ApplicationCommand, Box<dyn Error>>;
    async fn handle_command(
        &self,
        ctx: Context,
        command: ApplicationCommandInteraction,
    ) -> Result<(), Box<dyn Error>>;
    fn get_name(&self) -> String;
}

/// Handler for the application - will implement an EventHandler as _part_ of this
struct Handler;

#[async_trait]
impl EventHandler for Handler {
    // From docs:
    // Dispatched when an interaction is created (e.g a slash command was used or a button was clicked).
    // Provides the created interaction.
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        println!("{:#?}", interaction);
        if let Interaction::ApplicationCommand(command) = interaction {
            for application_command in APPLICATION_COMMANDS {
                if application_command.get_name() == command.data.name {
                    application_command
                        .handle_command(ctx.clone(), command)
                        .await
                        .expect("failed to handle application command");
                    return;
                }
            }

            command
                .create_interaction_response(&ctx.http, |response| {
                    response.interaction_response_data(|message| {
                        message.content(format!(
                            "Unhandled application command \"{}\"!",
                            command.data.name
                        ))
                    })
                })
                .await
                .expect("failed to send message");
        }
    }

    async fn guild_create(&self, ctx: Context, guild: Guild, _is_new: bool) {
        for application_command in APPLICATION_COMMANDS {
            {
                application_command
                    .register_command(ctx.clone(), &guild)
                    .await
                    .expect("failed to register application command");
                println!(
                    "Successfully registered application command: {}",
                    application_command.get_name()
                );
            }
        }
    }
}

#[tokio::main]
async fn main() {
    let application_id: u64 = env::var("APPLICATION_ID")
        .expect("Expected an application id in the environment")
        .parse()
        .expect("application id is not a valid id");

    // Load token into client
    let token = env::var("DISCORD_TOKEN").expect("Expected a token in the environment");
    let mut client = Client::builder(token)
        .event_handler(Handler)
        .application_id(application_id)
        .await
        .expect("Could not create client.");

    // Start listening on the client (single shard)
    if let Err(why) = client.start().await {
        println!("An error occurred starting the client: {:?}", why);
    }
}
