import os
from opentelemetry.sdk.resources import Resource, ResourceDetector
from opentelemetry.semconv.resource import ResourceAttributes
from observability.heroku_sementatic_conventions import HerokuSemanticConventions as Heroku


class HerokuResourceDetector(ResourceDetector):
    def detect(self) -> Resource:
        return Resource(
            {
                Heroku.RELEASE_CREATED_AT: os.getenv("HEROKU_RELEASE_CREATED_AT", ""),
                Heroku.SLUG_COMMIT: os.getenv("HEROKU_SLUG_COMMIT", ""),
                Heroku.APP_ID: os.getenv("HEROKU_APP_ID", ""),
                ResourceAttributes.SERVICE_NAME: os.getenv("HEROKU_APP_NAME", ""),
                ResourceAttributes.SERVICE_INSTANCE_ID: os.getenv("HEROKU_DYNO_ID", ""),
                ResourceAttributes.SERVICE_VERSION: os.getenv(
                    "HEROKU_RELEASE_VERSION", ""
                ),
                ResourceAttributes.CLOUD_PROVIDER: "heroku",
            }
        )
