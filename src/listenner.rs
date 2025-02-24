use crate::requests::handle_request;
use warp::Filter;

pub async fn listen_json() {
    // Define the POST /endpoint route that expects a JSON body
    let endpoint = warp::post()
        .and(warp::path("endpoint"))
        .and(warp::body::json())
        .and_then(handle_request);

    log::info!("Starting a warp service");
    // Start the server on localhost:19841
    warp::serve(endpoint).run(([127, 0, 0, 1], 19841)).await;
}
