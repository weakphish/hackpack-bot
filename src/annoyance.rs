use crate::ApplicationCommandHandler;

use serenity::async_trait;

use serenity::model::interactions::application_command::ApplicationCommandInteraction;
use serenity::model::{
    guild::Guild, interactions::application_command::ApplicationCommandOptionType,
};
use serenity::prelude::*;

use std::error::Error;

struct AnnoyanceRegisteredMarker;

impl TypeMapKey for AnnoyanceRegisteredMarker {
    type Value = ();
}

pub struct AnnoyanceApplicationCommand;

#[async_trait]
impl ApplicationCommandHandler for AnnoyanceApplicationCommand {
    async fn register_command(
        &self,
        ctx: Context,
        guild: &Guild,
    ) -> Result<
        serenity::model::interactions::application_command::ApplicationCommand,
        Box<dyn Error>,
    > {
        let mut data = ctx.data.write().await;
        if data.contains_key::<AnnoyanceRegisteredMarker>() {
            Err("annoyance application command already registered")?;
        } else {
            data.insert::<AnnoyanceRegisteredMarker>(())
        }

        guild
            .create_application_command(&ctx.http, |command| {
                command
                    .name("annoy")
                    .description("Annoy your least favorite user!")
                    .create_option(|option| {
                        option
                            .name("target")
                            .description("The target to annoy")
                            .kind(ApplicationCommandOptionType::User)
                            .required(true)
                    })
                    .create_option(|option| {
                        option
                            .name("repeat")
                            .description("Number of times to pester the target")
                            .kind(ApplicationCommandOptionType::Integer)
                            .required(true)
                    })
                    .create_option(|option| {
                        option
                            .name("interval")
                            .description("Time between messages (in seconds)")
                            .kind(ApplicationCommandOptionType::Integer)
                            .required(true)
                    })
            })
            .await
            .map_err(|e| e.into())
    }

    async fn handle_command(
        &self,
        ctx: Context,
        command: ApplicationCommandInteraction,
    ) -> Result<(), Box<dyn Error>> {
        command
            .create_interaction_response(&ctx.http, |response| {
                response
                    .interaction_response_data(|message| message.content("Annoyance incoming..."))
            })
            .await
            .map_err(|e| e.into())
    }

    fn get_name(&self) -> String {
        "annoy".to_string()
    }
}
