from langid32.settings import acquisition_target, language_target, load_config


def test_central_config_has_34_unique_target_languages():
    config = load_config()
    languages = config["project"]["languages"]
    assert len(languages) == 34
    assert len(set(languages)) == len(languages)


def test_source_and_language_overrides_are_explicit_and_inherit_defaults():
    config = load_config()
    assert acquisition_target(config, "leipzig_news", "hr") == 20000
    config["acquisition"]["source_language_overrides"]["leipzig_news.hr"] = 12345
    assert acquisition_target(config, "leipzig_news", "hr") == 12345
    assert language_target(config, "is") == 25000
    config["candidate"]["language_target_overrides"]["is"] = 24000
    assert language_target(config, "is") == 24000


def test_approved_source_language_scopes_and_jql_non_filtering_policy():
    config = load_config()
    assert set(config["acquisition"]["source_rules"]["leipzig_news"]["languages"]) == {
        "hr", "fi", "el", "mt", "sl", "is"
    }
    assert set(config["acquisition"]["source_rules"]["dgt_tm_2021"]["languages"]) == {
        "hr", "fi", "el", "mt", "sl"
    }
    assert config["candidate"]["final_sentences_per_language"] == 25000
    assert config["candidate"]["minimum_candidates_per_language"] == 35000
    assert config["jql"]["consensus_disagreement_penalty"] == 0.5
    assert config["jql"]["apply_quality_floor"] is False
    assert config["jql"]["selection_effect"] == "none"
