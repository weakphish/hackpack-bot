use std::env;

use serenity::async_trait;
use serenity::client::{Client, Context, EventHandler};
use serenity::model::channel::Message;
use serenity::framework::standard::{
    StandardFramework,
    CommandResult,
    macros::{
        command,
        group
    }
};

#[group]
struct General;

#[tokio::main]
async fn main() {
    // Load framework
    let framework = StandardFramework::new()
        .configure(|c| c.prefix("!"))
        .group(&GENERAL_GROUP);

    // Load token into client
    let token = env::var("DISCORD_TOKEN").expect("Token error"); 
    let mut client = Client::builder(token)
        .framework(framework)
        .await
        .expect("Could not create client."); 

    // Start listening on the client (single shard)
    if let Err(why) = client.start().await {
        println!("An error occurred starting the client: {:?}", why);
    }
}
