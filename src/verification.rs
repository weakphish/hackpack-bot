use crate::ApplicationCommandHandler;

use serenity::async_trait;

use serenity::model::interactions::application_command::ApplicationCommandInteraction;
use serenity::model::{
    guild::Guild, id::ChannelId, interactions::application_command::ApplicationCommandOptionType,
    user::User,
};
use serenity::prelude::*;

use std::collections::HashMap;
use std::error::Error;
use std::sync::Arc;

struct EmailVerificationInfo;

impl TypeMapKey for EmailVerificationInfo {
    type Value = Arc<RwLock<HashMap<(User, ChannelId), i64>>>;
}

pub struct EmailVerificationApplicationCommand;

#[async_trait]
impl ApplicationCommandHandler for EmailVerificationApplicationCommand {
    async fn register_command(
        &self,
        ctx: Context,
        guild: &Guild,
    ) -> Result<
        serenity::model::interactions::application_command::ApplicationCommand,
        Box<dyn Error>,
    > {
        let mut data = ctx.data.write().await;
        if data.contains_key::<EmailVerificationInfo>() {
            Err("email verification application command already registered")?;
        } else {
            data.insert::<EmailVerificationInfo>(Arc::new(RwLock::new(HashMap::new())))
        }

        guild
            .create_application_command(&ctx.http, |command| {
                command
                    .name("verify")
                    .description("Verify your email address")
                    .create_option(|option| {
                        option
                            .name("email")
                            .description("Your email address")
                            .kind(ApplicationCommandOptionType::String)
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
                response.interaction_response_data(|message| {
                    message.content("Congrats! You are now verified! Ish...")
                })
            })
            .await
            .map_err(|e| e.into())
    }

    fn get_name(&self) -> String {
        "verify".to_string()
    }
}
