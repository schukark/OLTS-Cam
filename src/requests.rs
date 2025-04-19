//! Requests module takes care of all connections with the python desktop client
//! (get/post requests to the API endpoint)

use crate::errors::RequestError;
use crate::models::*;
use anyhow::Result;

use lazy_static::lazy_static;
use reqwest::Client;

lazy_static! {
    static ref CLIENT: Client = Client::new();
}

/// Function that posts a 'change settings' request and reports if any error occured
pub async fn change_settings(address_str: &str, settings: Settings) -> Result<()> {
    let request_url = format!("http://{address_str}/settings",);
    let response = CLIENT.post(request_url).json(&settings).send().await?;

    match response.status().as_u16() {
        200 => Ok(()),
        400 => Err(RequestError::NoSuchReceiver.into()),
        401 => Err(RequestError::NoSuchSetting.into()),
        _ => Err(RequestError::UnknownError.into()),
    }
}

/// Function that gets a current settings and reports if any error occured
pub async fn get_settings(address_str: &str, receiver: Receiver) -> Result<Settings> {
    let request_url = format!("http://{address_str}/settings/{receiver}");

    let response = CLIENT.get(request_url).send().await?;

    let settings = response.json().await?;

    Ok(settings)
}

/// Function that gets an object by its name and reports if any error occured
pub async fn get_object(address_str: &str, name: String) -> Result<ObjectPhoto> {
    let request_url = format!("http://{address_str}/object/{name}");

    let response = CLIENT.get(request_url).send().await?;

    let object = response.json().await?;

    Ok(object)
}

/// Mock tests to verify the behavior
#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;
    mod change_settings_tests {
        use super::*;

        #[tokio::test]
        async fn test_no_such_setting() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            dbg!(&host_with_port);

            let mock = server
                .mock("POST", "/settings")
                .with_status(401)
                .with_header("content-type", "application/json")
                .create_async()
                .await;

            let settings = serde_json::from_str(
                r#"{"receiver": "camera","settings": [{"key": "FPS","value": "30"}]}"#,
            )?;

            assert!(change_settings(&host_with_port, settings).await.is_err());
            mock.assert_async().await;

            Ok(())
        }

        #[tokio::test]
        async fn test_correct_case() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("POST", "/settings")
                .with_status(200)
                .with_header("content-type", "application/json")
                .create_async()
                .await;

            let settings = serde_json::from_str(
                r#"{"receiver": "camera","settings": [{"key": "FPS","value": "30"}]}"#,
            )?;

            assert!(change_settings(&host_with_port, settings).await.is_ok());
            mock.assert_async().await;

            Ok(())
        }
    }

    mod get_settings_test {
        use super::*;

        #[tokio::test]
        async fn test_correct() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("POST", "/settings")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(r#"{"receiver": "camera","settings": [{"key": "FPS","value": "30"}]}"#)
                .create_async()
                .await;

            let settings = serde_json::from_str(
                r#"{"receiver": "camera","settings": [{"key": "FPS","value": "30"}]}"#,
            )?;

            assert_eq!(
                get_settings(&host_with_port, Receiver::Camera).await?,
                settings
            );
            mock.assert_async().await;

            Ok(())
        }
    }
}
