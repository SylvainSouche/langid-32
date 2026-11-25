import pytest

from langid32.settings import acquisition_target, language_target, load_config


def test_central_config_has_34_unique_target_languages():
    config = load_config()
    languages = config["project"]["languages"]
    assert len(languages) == 34
    assert len(set(languages)) == len(languages)


def test_source_and_language_overrides_are_explicit_and_inherit_defaults():
    config = load_config()
    assert acquisition_target(config, "leipzig_news", "hr") == 20000
    assert acquisition_target(config, "fineweb2:hrv_Latn", "hr") == 20000
    config["acquisition"]["source_language_overrides"]["fineweb2.hr"] = 12345
    assert acquisition_target(config, "fineweb2:hrv_Latn", "hr") == 12345
    assert acquisition_target(config, "macocu_hr_2.0", "hr") == 20000
    assert acquisition_target(config, "parlamint_is", "is") == 20000
    assert acquisition_target(config, "greynir_copper", "is") == 20000
    assert acquisition_target(config, "greynir_silver", "is") == 20000
    with pytest.raises(ValueError):
        acquisition_target(config, "greynir_gold_dev_test", "is")
    with pytest.raises(ValueError):
        acquisition_target(config, "fineweb2:cat_Latn", "ca")
    with pytest.raises(ValueError):
        acquisition_target(config, "fineweb", "en")
    with pytest.raises(ValueError):
        acquisition_target(config, "unregistered_source", "hr")
    config["acquisition"]["source_language_overrides"]["leipzig_news.hr"] = 12345
    assert acquisition_target(config, "leipzig_news", "hr") == 12345
    assert language_target(config, "is") == 30000
    config["candidate"]["language_target_overrides"]["is"] = 24000
    assert language_target(config, "is") == 24000


def test_approved_source_scopes_and_deferred_final_selection_policy():
    config = load_config()
    assert set(config["acquisition"]["source_rules"]["leipzig_news"]["languages"]) == {
        "hr", "fi", "el", "mt", "sl", "is"
    }
    assert set(config["acquisition"]["source_rules"]["dgt_tm_2021"]["languages"]) == {
        "hr", "fi", "el", "mt", "sl"
    }
    assert config["acquisition"]["first_pass_target_per_source_language"] == 20000
    assert config["candidate"]["final_sentences_per_language"] == 30000
    assert config["candidate"]["final_selection_status"] == "deferred_pending_user_review"
    assert config["candidate"]["source_balance"]["enabled"] is False
    assert config["jql"]["consensus_disagreement_penalty"] == 0.5
    assert config["jql"]["embedder_model"] == "Snowflake/snowflake-arctic-embed-m-v2.0"
    assert config["jql"]["head_repository"] == "JQL-AI/JQL-Edu-Heads"
    assert set(config["jql"]["head_checkpoints"]) == {"gemma", "mistral", "llama"}
    assert config["jql"]["score_decimal_places"] == 6
    assert config["jql"]["prune_bottom_quantile"] == 0.25
    assert config["jql"]["pruning_scope"] == "global_all_languages_after_full_corpus_normalization"
    assert config["jql"]["final_selection_requires_user_approval"] is True
    assert config["quality"]["initial_capitalization"] == "record_flag_only"
    assert config["quality"]["terminal_punctuation"] == "record_flag_only"
