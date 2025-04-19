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

    match response.status().as_u16() {
        200 => Ok(response.json().await?),
        _ => Err(RequestError::UnknownError.into()),
    }
}

/// Function that gets an object by its name and reports if any error occured
pub async fn get_object(address_str: &str, name: &str) -> Result<ObjectPhoto> {
    let request_url = format!("http://{address_str}/object/{name}");

    let response = CLIENT.get(request_url).send().await?;

    dbg!(&response);

    match response.status().as_u16() {
        200 => Ok(response.json().await?),
        400 => Err(RequestError::ImageTooBig.into()),
        _ => Err(RequestError::UnknownError.into()),
    }
}

/// Function that requests the current state of the camera feed
pub async fn get_objects(address_str: &str) -> Result<ObjectPhoto> {
    let request_url = format!("http://{address_str}/objects");

    let response = CLIENT.get(request_url).send().await?;

    match response.status().as_u16() {
        200 => Ok(response.json().await?),
        400 => Err(RequestError::ImageTooBig.into()),
        _ => Err(RequestError::UnknownError.into()),
    }
}

/// Mock tests to verify the behavior
#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Result;

    /// Tests for the change_settings() method
    mod change_settings_tests {
        use super::*;

        /// Tests whether a no such setting case is handled correctly
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
                "{\"receiver\":\"camera\",\"settings\":[{\"key\":\"FPS\",\"value\":\"30\"}]}",
            )?;

            assert!(change_settings(&host_with_port, settings).await.is_err());
            mock.assert_async().await;

            Ok(())
        }

        /// Tests the correct behavior
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

    /// Tests for the get_settings() method
    mod get_settings_test {
        use super::*;

        /// Tests the correct behavior
        #[tokio::test]
        async fn test_correct() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("GET", "/settings/camera")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body(
                    "{\"receiver\":\"camera\",\"settings\":[{\"key\":\"FPS\",\"value\":\"30\"}]}",
                )
                .create_async()
                .await;

            let settings = serde_json::from_str(
                "{\"receiver\":\"camera\",\"settings\":[{\"key\":\"FPS\",\"value\":\"30\"}]}",
            )?;

            assert_eq!(
                get_settings(&host_with_port, Receiver::Camera).await?,
                settings
            );
            mock.assert_async().await;

            Ok(())
        }
    }

    /// Tests for the get_object() method
    mod get_object_tests {
        use super::*;

        /// Tests whether the behavior when the image is too big is correct
        #[tokio::test]
        async fn test_image_too_big() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("GET", "/object/apple")
                .with_status(400)
                .with_header("content-type", "application/json")
                .with_body("{\"height\":224,\"width\":224,\"image\":\"aboba\"}")
                .create_async()
                .await;

            assert!(get_object(&host_with_port, "apple").await.is_err());
            mock.assert_async().await;

            Ok(())
        }

        /// Correct behavior test
        #[tokio::test]
        async fn test_correct_case() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("GET", "/object/apple")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body("{\"height\":224,\"width\":224,\"image\":\"aboba\"}")
                .create_async()
                .await;

            assert!(get_object(&host_with_port, "apple").await.is_ok());
            mock.assert_async().await;

            Ok(())
        }
    }

    /// Tests for the get_objects() method
    mod get_objects_tests {
        use super::*;

        /// Tests the situation when the file size is too big
        #[tokio::test]
        async fn test_image_too_big() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("GET", "/objects")
                .with_status(400)
                .with_header("content-type", "application/json")
                .with_body("{\"height\":224,\"width\":224,\"image\":\"aboba\"}")
                .create_async()
                .await;

            assert!(get_objects(&host_with_port).await.is_err());
            mock.assert_async().await;

            Ok(())
        }

        /// Tests the expected behavior
        #[tokio::test]
        async fn test_correct_case() -> Result<()> {
            let mut server = mockito::Server::new_async().await;

            let host_with_port = server.host_with_port();

            let mock = server
                .mock("GET", "/objects")
                .with_status(200)
                .with_header("content-type", "application/json")
                .with_body("{\"height\":224,\"width\":224,\"image\":\"aboba\"}")
                .create_async()
                .await;

            assert!(get_objects(&host_with_port).await.is_ok());
            mock.assert_async().await;

            Ok(())
        }
    }
}
