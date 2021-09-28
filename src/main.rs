//! This is the Rust implementation of a Discord bot, initially designed for
//! HackPack.

#![deny(missing_docs)]
#![deny(rustdoc::broken_intra_doc_links)]
#![deny(rustdoc::private_intra_doc_links)]

pub mod ping;

use ping::PingApplicationCommand;

use serenity::client::{Context, EventHandler};
use serenity::model::interactions::application_command::ApplicationCommandInteraction;
use serenity::model::{
    guild::Guild,
    interactions::{application_command::ApplicationCommand, Interaction},
};

use serenity::{async_trait, Client};

use std::env;
use std::error::Error;

/// A global list of application commands which will be registered for each
/// found [`Guild`] and used to handle any incoming
/// [`ApplicationCommandInteraction`].
pub const APPLICATION_COMMANDS: &[&(dyn ApplicationCommandHandler + Sync)] =
    &[&PingApplicationCommand];

/// This trait represents a handler for an [`ApplicationCommandInteraction`].
/// Unit structs implementing this trait are stored in [`APPLICATION_COMMANDS`],
/// which are then registered and handled elsewhere.
///
/// Methods associated with this trait may find it useful to utilize the passed
/// [`Context::data`]. This field is extremely useful to persist data across
/// callback invocations. It is recommended that you only index
/// [`Context::data`] with private struct types, to avoid potentially
/// conflicting data storage across different application commands.
///
/// We may add some boilerplate macros for the automatic creation of
/// [`APPLICATION_COMMANDS`] and registration of [`ApplicationCommandHandler`]s,
/// in the future.
///
/// [`get_name`]: Self::get_name
#[async_trait]
pub trait ApplicationCommandHandler {
    /// Called to register a a new application command. This method should
    /// handle registration of a new application command in the given
    /// [`Guild`], with the name returned by [`get_name`]. This method returns
    /// the newly-created [`Application Command`].
    ///
    /// # Errors
    ///
    /// This method returns an error if there is any issue registering the new
    /// application command. This method also returns an error if it
    /// detects that this command has already been registered for the given
    /// guild.
    ///
    /// [`get_name`]: Self::get_name
    /// [`Application Command`]: ApplicationCommand
    async fn register_command(
        &self,
        ctx: &Context,
        guild: &Guild,
    ) -> Result<ApplicationCommand, Box<dyn Error>>;

    /// Called to handle an incoming application command with a name that
    /// matches this impl's [`get_name`].
    ///
    /// This method must send some sort of response to the given
    /// [`ApplicationCommandInteraction`], using
    /// [`create_interaction_response`].
    ///
    /// # Errors
    ///
    /// This method returns an error if there is any issue handling this
    /// application command. This may be due to the provided application
    /// command information having unexpected arguments, an issue sending a
    /// response to the application command, or any other issue specific to a
    /// given application command.
    ///
    /// [`get_name`]: Self::get_name
    /// [`create_interaction_response`]:
    /// ApplicationCommandInteraction::create_interaction_response
    async fn handle_command(
        &self,
        ctx: &Context,
        command: ApplicationCommandInteraction,
    ) -> Result<(), Box<dyn Error>>;

    /// Gets the name of the application command associated with this impl. This
    /// function must always return the same value for any given concrete impl.
    fn get_name(&self) -> String;
}

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    // Dispatched when an interaction is created (e.g. a slash command was used or a
    // button was clicked). Provides the created interaction.
    //
    // When a new interaction is created, we check its name against all registered
    // application commands (in [`APPLICATION_COMMANDS`]). If any match,
    // we dispatch that application command's handler.
    //
    // # Panics
    //
    // Panics if none of the available [`APPLICATION_COMMANDS`] match, or if we run
    // into an error handling this application command.
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        println!("{:#?}", interaction);
        if let Interaction::ApplicationCommand(command) = interaction {
            for application_command in APPLICATION_COMMANDS {
                if application_command.get_name() == command.data.name {
                    application_command
                        .handle_command(&ctx, command)
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

    // Dispatched when a guild is created; or an existing guild's data is sent to
    // us.
    // Provides the guild's data and whether the guild is new.
    //
    // When we detect that a guild was created (either an existing guild has just
    // become available to this bot or a guild was actually created),
    // register all [`APPLICATION_COMMANDS`] under the newly detected guild.
    //
    // # Panics
    //
    // Panics if there was an error registering any of [`APPLICATION_COMMANDS`].
    async fn guild_create(&self, ctx: Context, guild: Guild, _is_new: bool) {
        for application_command in APPLICATION_COMMANDS {
            {
                application_command
                    .register_command(&ctx, &guild)
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

/// We expect APPLICATION_ID and DISCORD_TOKEN for the bot application to be
/// passed to the program at startup, via environment variables.
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let application_id: u64 = env::var("APPLICATION_ID")
        .map_err(|_| "Expected APPLICATION_ID in the environment")?
        .parse()
        .map_err(|_| "APPLICATION_ID is not a valid id")?;

    let token =
        env::var("DISCORD_TOKEN").map_err(|_| "expected DISCORD_TOKEN in the environment")?;
    let mut client = Client::builder(token)
        .event_handler(Handler)
        .application_id(application_id)
        .await
        .map_err(|_| "could not create client")?;

    client
        .start()
        .await
        .map_err(|err| format!("an error occured starting the client: {:?}", err).into())
}
