from zerver.lib.test_classes import WebhookTestCase


class ThinkstHookTests(WebhookTestCase):
    STREAM_NAME = "travis"
    URL_TEMPLATE = "/api/v1/external/thinkst?stream={stream}&api_key={api_key}"
    FIXTURE_DIR_NAME = "thinkst"

    def test_canary_alert(self) -> None:
        """
        Canary alerts are generated by Thinkst's hardware or virtual canaries.
        """
        expected_message = (
            "**:alert: Canary has been triggered!**\n\n"
            "On 2020-06-09 13:59:38 (UTC), `0000000testnode` was triggered "
            "from `2.2.2.2` (`attacker-ip.local`):\n\n"
            "> This is a dummy incident."
        )

        self.send_and_test_stream_message(
            "canary_alert",
            "canary alert - 0000000testnode",
            expected_message,
            content_type="application/x-www-form-urlencoded",
        )

    def test_canary_alert_no_reverse_dns(self) -> None:
        """
        Canary alerts are generated by Thinkst's hardware or virtual canaries.
        """
        expected_message = (
            "**:alert: Canary has been triggered!**\n\n"
            "On 2020-06-09 13:59:38 (UTC), `0000000testnode` was triggered "
            "from `2.2.2.2`:\n\n"
            "> This is a dummy incident."
        )

        self.send_and_test_stream_message(
            "canary_alert_no_reverse_dns",
            "canary alert - 0000000testnode",
            expected_message,
            content_type="application/x-www-form-urlencoded",
        )

    def test_canary_alert_with_specific_topic(self) -> None:
        """
        Canary alerts are generated by Thinkst's hardware or virtual canaries.
        """
        self.url = self.build_webhook_url(topic="foo")
        expected_message = (
            "**:alert: Canary `0000000testnode` has been triggered!**\n\n"
            "On 2020-06-09 13:59:38 (UTC), `0000000testnode` was triggered "
            "from `2.2.2.2` (`attacker-ip.local`):\n\n"
            "> This is a dummy incident."
        )

        self.send_and_test_stream_message(
            "canary_alert", "foo", expected_message, content_type="application/x-www-form-urlencoded",
        )

    def test_canarytoken_new(self) -> None:
        """
        Thinkst Canarytokens are simple tripwires for detecting when resources have been accessed.
        """
        expected_message = (
            "**:alert: Canarytoken has been triggered on 2020-06-09 14:04:39!**\n\n"
            "> Congrats! The newly saved webhook works \n\n"
            "[Manage this canarytoken](http://example.com/test/url/for/webhook)"
        )

        self.send_and_test_stream_message(
            "canarytoken_new",
            "canarytoken alert",
            expected_message,
            content_type="application/x-www-form-urlencoded",
        )

    def test_canarytoken_real(self) -> None:
        """
        Thinkst Canarytokens are simple tripwires for detecting when resources have been accessed.
        """
        expected_message = (
            "**:alert: Canarytoken has been triggered on 2020-06-09 14:04:47 (UTC)!**\n\n"
            "> Canarytoken example \n\n"
            "[Manage this canarytoken](https://canarytokens.org/manage?token=foo&auth=bar)"
        )

        self.send_and_test_stream_message(
            "canarytoken_real",
            "canarytoken alert",
            expected_message,
            content_type="application/x-www-form-urlencoded",
        )

    def test_canarytoken_with_specific_topic(self) -> None:
        """
        Thinkst Canarytokens are simple tripwires for detecting when resources have been accessed.
        """
        self.url = self.build_webhook_url(topic="foo")
        expected_message = (
            "**:alert: Canarytoken has been triggered on 2020-06-09 14:04:47 (UTC)!**\n\n"
            "> Canarytoken example \n\n"
            "[Manage this canarytoken](https://canarytokens.org/manage?token=foo&auth=bar)"
        )

        self.send_and_test_stream_message(
            "canarytoken_real", "foo", expected_message, content_type="application/x-www-form-urlencoded",
        )
