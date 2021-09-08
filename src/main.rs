use std::env;

use serenity::client::Client;

#[tokio::main]
async fn main() {
    // Load token into client
    let token = env::var("DISCORD_TOKEN").expect("Token error"); 
    let mut client = Client::builder(token).await.expect("Could not create client."); 

    // Start listening on the client (single shard)
    if let Err(why) = client.start().await {
        println!("An error occurred starting the client: {:?}", why);
    }
}
