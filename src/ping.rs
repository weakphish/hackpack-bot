//! Module containing the `/ping` application command.

use crate::ApplicationCommandHandler;

use serenity::async_trait;

use serenity::model::guild::Guild;
use serenity::model::id::GuildId;
use serenity::model::interactions::application_command::ApplicationCommandInteraction;
use serenity::prelude::*;

use std::collections::HashSet;
use std::error::Error;

/// Keeps track of guilds for which this application command handler has already
/// been registered. When this application command is registered to a new guild,
/// the corresponding [`GuildId`] is added to [`PingRegisteredInfo::Value`]
#[doc(hidden)]
struct PingRegisteredInfo;

impl TypeMapKey for PingRegisteredInfo {
    type Value = HashSet<GuildId>;
}

/// A basic [`ApplicationCommandHandler`], intended for demonstration purposes.
///
/// This [`ApplicationCommandHandler`] simply replies to `/ping` with
/// `Pong, <user>!`.
pub struct PingApplicationCommand;

#[async_trait]
impl ApplicationCommandHandler for PingApplicationCommand {
    async fn register_command(
        &self,
        ctx: &Context,
        guild: &Guild,
    ) -> Result<
        serenity::model::interactions::application_command::ApplicationCommand,
        Box<dyn Error>,
    > {
        let mut data = ctx.data.write().await;
        // Ensure that this application command has not already been registered for the
        // given guild, according to the global application context's data.
        if !data
            .entry::<PingRegisteredInfo>()
            .or_default()
            .insert(guild.id)
        {
            return Err(format!(
                "ping application command already registered for {}",
                guild.name,
            )
            .into());
        }

        guild
            .create_application_command(&ctx.http, |command| {
                command
                    .name(self.get_name())
                    .description("Check if this bot is working")
            })
            .await
            .map_err(|e| e.into())
    }

    async fn handle_command(
        &self,
        ctx: &Context,
        command: ApplicationCommandInteraction,
    ) -> Result<(), Box<dyn Error>> {
        // This application command simply responds to any incoming request with `Pong,
        // <user>!`.
        command
            .create_interaction_response(&ctx.http, |response| {
                response.interaction_response_data(|message| {
                    message.content(format!("Pong, {}!", command.user.mention()))
                })
            })
            .await
            .map_err(|e| e.into())
    }

    fn get_name(&self) -> String {
        "ping".to_string()
    }
}
