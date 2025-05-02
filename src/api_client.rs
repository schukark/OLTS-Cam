//! Requests module takes care of all connections with the python desktop client
//! (get/post requests to the API endpoint)

use crate::errors::{ModelError, RequestError};
use crate::models::*;
use anyhow::Result;

use reqwest::Client;

#[derive(Clone)]
/// Struct that represents an http client responsible for the API endpoint requesting
pub struct ApiClient {
    /// Base url of the API endpoint (default: 127.0.0.1)
    base_url: String,

    /// API andpoint Client
    client: Client,
}

impl ApiClient {
    /// Default constructor for the Api client
    pub fn new(base_url: impl Into<String>) -> Self {
        ApiClient {
            base_url: base_url.into(),
            client: Client::new(),
        }
    }

    /// Function that posts a 'change settings' request and reports if any error occured
    pub async fn change_settings(&self, settings: Settings) -> Result<()> {
        let request_url = format!("http://{}/settings", self.base_url);
        let response = self.client.post(request_url).json(&settings).send().await?;

        log::trace!("'Change settings' received a response from an api server");

        match response.status().as_u16() {
            200 => {
                log::trace!("Response: 200");
                Ok(())
            }
            401 => {
                log::trace!("Response: 401");
                Err(RequestError::NoSuchSetting.into())
            }
            422 => {
                log::trace!("Response: 422");
                Err(RequestError::NoSuchReceiver.into())
            }
            x => {
                log::trace!("Response: {x}");
                Err(RequestError::UnknownError.into())
            }
        }
    }

    /// Function that gets a current settings and reports if any error occured
    pub async fn get_settings(&self, receiver: Receiver) -> Result<Settings> {
        let request_url = format!("http://{}/settings/{}", self.base_url, receiver);
        let response = self.client.get(request_url).send().await?;

        log::trace!("'Get settings' received a response from an api server");

        match response.status().as_u16() {
            200 => {
                log::trace!("Response: 200");
                match response.json().await {
                    Ok(settings) => {
                        log::trace!("Settings parsed");
                        Ok(settings)
                    }
                    Err(e) => {
                        log::trace!("Error parsing settings: {e}");
                        Err(ModelError::InvalidSettings.into())
                    }
                }
            }
            422 => {
                log::trace!("Response: 422");
                Err(RequestError::NoSuchReceiver.into())
            }
            x => {
                log::trace!("Response: {x}");
                Err(RequestError::UnknownError.into())
            }
        }
    }

    /// Function that gets an object by its name and reports if any error occured
    pub async fn get_object(&self, name: &str) -> Result<ObjectPhoto> {
        let request_url = format!("http://{}/object/{}", self.base_url, name);
        let response = self.client.get(request_url).send().await?;

        log::trace!("'Get object' received a response from an api server");

        match response.status().as_u16() {
            200 => {
                log::trace!("Response: 200");
                Ok(response.json().await?)
            }
            x => {
                log::trace!("Response: {x}");
                Err(RequestError::UnknownError.into())
            }
        }
    }

    /// Function that requests the current state of the camera feed
    pub async fn get_objects(&self) -> Result<ObjectPhoto> {
        let request_url = format!("http://{}/objects", self.base_url);
        let response = self.client.get(request_url).send().await?;

        log::trace!("'Get objects' received a response from an api server");

        match response.status().as_u16() {
            200 => {
                log::trace!("Response: 200");
                Ok(response.json().await?)
            }
            x => {
                log::trace!("Response: {x}");
                Err(RequestError::UnknownError.into())
            }
        }
    }
}

/// Mock tests to verify the behavior
#[cfg(test)]
#[cfg_attr(coverage_nightly, coverage(off))]
mod tests {
    use super::*;
    use anyhow::Result;
    use httpmock::prelude::*;

    /// Tests for the change_settings() method
    mod change_settings_tests {
        use super::*;

        /// Tests whether a no such setting case is handled correctly
        #[tokio::test]
        async fn test_no_such_setting() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(POST).path("/settings");
                then.status(401).header("content-type", "application/json");
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let api_client = ApiClient::new(host_with_port);

            let settings = serde_json::from_str(
                "{\"receiver\":\"db\",\"settings\":[{\"key\":\"dummy_key\",\"value\":\"dummy_value\"}]}",
            )?;

            let result = api_client.change_settings(settings).await;
            assert!(result.is_err());
            if let Some(x) = result.unwrap_err().downcast_ref::<RequestError>() {
                assert_eq!(*x, RequestError::NoSuchSetting);
            } else {
                panic!("Expected RequestError::NoSuchSetting");
            }
            mock.assert_async().await;

            Ok(())
        }

        /// Tests whether a no such receiver case is handled correctly
        #[tokio::test]
        async fn test_no_such_receiver() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(POST).path("/settings");
                then.status(422).header("content-type", "application/json");
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let api_client = ApiClient::new(host_with_port);

            let settings = serde_json::from_str(
                "{\"receiver\":\"camera\",\"settings\":[{\"key\":\"FPS\",\"value\":\"30\"}]}",
            )?;

            let result = api_client.change_settings(settings).await;
            assert!(result.is_err());
            if let Some(x) = result.unwrap_err().downcast_ref::<RequestError>() {
                assert_eq!(*x, RequestError::NoSuchReceiver);
            } else {
                panic!("Expected RequestError::NoSuchReceiver");
            }
            mock.assert_async().await;

            Ok(())
        }

        /// Tests the correct behavior
        #[tokio::test]
        async fn test_correct_case() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(POST).path("/settings");
                then.status(200).header("content-type", "application/json");
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let api_client = ApiClient::new(host_with_port);

            let settings = serde_json::from_str(
                r#"{"receiver":"camera","settings":[{"key":"FPS","value":"30"}]}"#,
            )?;

            let result = api_client.change_settings(settings).await;
            assert!(result.is_ok());
            mock.assert_async().await;

            Ok(())
        }
    }

    /// Tests for the get_settings() method
    mod get_settings_test {
        use super::*;

        /// Tests the situation when the receiver is incorrect
        #[tokio::test]
        async fn test_incorrect_receiver() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(GET).path("/settings/camera");
                then.status(422)
                    .header("content-type", "application/json")
                    .body(
                    "{\"receiver\":\"camera\",\"settings\":[{\"key\":\"FPS\",\"value\":\"30\"}]}",
                );
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let api_client = ApiClient::new(host_with_port);
            let result = api_client.get_settings(Receiver::Camera).await;
            // camera is correct, but as api says, server is always right

            assert!(result.is_err());
            mock.assert_async().await;

            Ok(())
        }

        /// Tests the correct behavior
        #[tokio::test]
        async fn test_correct() -> Result<()> {
            let server = MockServer::start_async().await;

            let mock = server.mock(|when, then| {
                when.method(GET).path("/settings/fs");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(
                    "{\"receiver\":\"fs\",\"settings\":[{\"key\":\"limit\",\"value\":\"30G\"}]}",
                );
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let api_client = ApiClient::new(host_with_port);

            let settings = serde_json::from_str(
                "{\"receiver\":\"fs\",\"settings\":[{\"key\":\"limit\",\"value\":\"30G\"}]}",
            )?;

            let result = api_client.get_settings(Receiver::Camera).await;
            assert!(result.is_ok());
            assert_eq!(result.unwrap(), settings);
            mock.assert_async().await;

            Ok(())
        }
    }

    /// Tests for the get_object() method
    mod get_object_tests {
        use super::*;

        /// Correct behavior test
        #[tokio::test]
        async fn test_correct_case() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "{\"height\":224,\"width\":224,\"image\":\"aboba\"}";

            let mock = server.mock(|when, then| {
                when.method(GET).path("/object/apple");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let object_photo = serde_json::from_str(body)?;

            let api_client = ApiClient::new(host_with_port);

            let response = api_client.get_object("apple").await;

            assert_eq!(response?, object_photo);
            mock.assert_async().await;

            Ok(())
        }
    }

    /// Tests for the get_objects() method
    mod get_objects_tests {
        use super::*;

        /// Tests the expected behavior
        #[tokio::test]
        async fn test_correct_case() -> Result<()> {
            let server = MockServer::start_async().await;

            let body = "{\"height\":224,\"width\":224,\"image\":\"aboba\"}";

            let mock = server.mock(|when, then| {
                when.method(GET).path("/objects");
                then.status(200)
                    .header("content-type", "application/json")
                    .body(body);
            });

            let host_with_port = server.host() + ":" + &server.port().to_string();

            let object_photo = serde_json::from_str(body)?;

            let api_client = ApiClient::new(host_with_port);

            let response = api_client.get_objects().await;

            assert_eq!(response?, object_photo);
            mock.assert_async().await;

            Ok(())
        }
    }
}
