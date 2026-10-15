import pytest
from app import hiring_files


@pytest.mark.parametrize(
    ("title", "slug"),
    [
        ("CEO", "ceo"),
        ("Head of Sales!", "head-of-sales"),
        ("  Data  Engineer ", "data-engineer"),
    ],
)
def test_slugify_makes_a_folder_safe_name(title: str, slug: str) -> None:
    assert hiring_files.slugify(title) == slug


@pytest.mark.parametrize("slug", ["../etc", "a/b", "", "-leading", "UPPER"])
def test_unsafe_slugs_are_rejected(slug: str, tmp_path) -> None:
    assert not hiring_files.is_valid_slug(slug)
    with pytest.raises(ValueError):
        hiring_files.job_description_path(tmp_path, slug)


def test_write_then_read_round_trip(tmp_path) -> None:
    hiring_files.write_job_description(
        tmp_path, "ceo", "# CEO\n\nText.", ai_output_id=7
    )

    text = hiring_files.read_job_description(tmp_path, "ceo")

    assert text is not None
    assert text.startswith("# CEO\n\nText.\n")
    assert "AI output 7" in text
