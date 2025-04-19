//! Requests module takes care of all connections with the python desktop client
//! (get/post requests to the API endpoint)

use crate::models::*;

use crate::{ADDRESS, CLIENT, PORT};
use reqwest::Error;

/// Function that posts a 'change settings' request and reports if any error occured
pub async fn change_settings(settings: Settings) -> Result<(), Error> {
    let request_url = format!("http://{ADDRESS}:{PORT}/settings",);
    CLIENT.post(request_url).json(&settings).send().await?;

    Ok(())
}

/// Function that gets a current settings and reports if any error occured
pub async fn get_settings(receiver: Receiver) -> Result<Settings, Error> {
    let request_url = format!("http://{ADDRESS}:{PORT}/settings/{receiver}");

    let response = CLIENT.get(request_url).send().await?;

    let settings = response.json().await?;

    Ok(settings)
}

/// Function that gets an object by its name and reports if any error occured
pub async fn get_object(name: String) -> Result<ObjectPhoto, Error> {
    let request_url = format!("http://{ADDRESS}:{PORT}/object/{name}");

    let response = CLIENT.get(request_url).send().await?;

    let object = response.json().await?;

    Ok(object)
}
