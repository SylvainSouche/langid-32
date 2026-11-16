import tarfile

from langid32.common_voice_extract import extract_text_tsv


def test_extracts_only_validated_sentence_file(tmp_path):
    archive_path = tmp_path / "common-voice-fr.tar.gz"
    payload = b"sentence_id\tsentence\tis_used\n1\tUne phrase de test.\ttrue\n"
    with tarfile.open(archive_path, "w:gz") as archive:
        import io
        info = tarfile.TarInfo("cv-corpus-27/fr/validated_sentences.tsv")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))
        audio = b"not actually audio"
        audio_info = tarfile.TarInfo("cv-corpus-27/fr/clips/clip.mp3")
        audio_info.size = len(audio)
        archive.addfile(audio_info, io.BytesIO(audio))
    result = extract_text_tsv("fr", archive_path, tmp_path / "out")
    extracted = tmp_path / "out/fr/validated_sentences.tsv"
    assert extracted.read_bytes() == payload
    assert result["locale"] == "fr"
    assert result["tsv_bytes"] == len(payload)
    assert not (tmp_path / "out/fr/clips/clip.mp3").exists()
