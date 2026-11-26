import pytest

from langid32.settings import acquisition_target, language_target, load_config, validate_jql_policy


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
    assert acquisition_target(config, "gaois_irish_legislation", "ga") == 50000
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

def test_jql_contract_is_locked_to_full_pool_global_quartile_and_deferred_selection():
    config = load_config()
    assert config["jql"]["assessment_all_candidate_rows"] is True
    assert config["jql"]["assessment_sample_per_language"] == 0
    assert config["jql"]["max_rows"] == 0
    assert config["jql"]["judges"] == ["gemma", "mistral", "llama"]
    assert config["jql"]["out_of_training_languages"] == ["ar", "ja", "ko", "zh", "nb", "nn"]
    assert config["jql"]["prune_bottom_quantile"] == 0.25
    assert config["jql"]["max_seconds"] == 3600
    assert config["jql"]["assessment_batch_size"] == 2000
    assert config["jql"]["shard_batch_rows"] == 8192
    assert config["jql"]["inference_batch_size"] == 8
    assert config["jql"]["inference_dtype"] == "bfloat16"
    assert config["jql"]["python_version"] == "3.11"
    assert config["jql"]["torch_version"] == "2.6.0"
    assert config["jql"]["transformers_version"] == "4.44.2"
    assert config["jql"]["huggingface_hub_version"] == "0.26.5"
    assert config["jql"]["shard_count"] == 8
    assert config["jql"]["max_parallel_shards"] == 4
    assert config["jql"]["job_timeout_minutes"] == 360
    assert config["jql"]["upload_buffer_minutes"] == 10
    assert config["candidate"]["source_balance"]["preferred_share"] == 0.30
    assert config["candidate"]["source_balance"]["hard_max_share"] == 0.50


def test_jql_policy_rejects_sampling_and_per_language_pruning():
    config = load_config()
    config["jql"]["assessment_all_candidate_rows"] = False
    with pytest.raises(ValueError, match="assess every"):
        validate_jql_policy(config)
    config = load_config()
    config["jql"]["prune_bottom_quantile"] = 0.20
    with pytest.raises(ValueError, match="global bottom 25"):
        validate_jql_policy(config)


def test_jql_policy_rejects_automatic_final_selection():
    config = load_config()
    config["candidate"]["source_balance"]["enabled"] = True
    with pytest.raises(ValueError, match="must remain disabled"):
        validate_jql_policy(config)
