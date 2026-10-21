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

    assert text == "# CEO\n\nText.\n"
    written = (tmp_path / "ceo" / "ceo.md").read_text(encoding="utf-8")
    assert written.endswith(
        "<!-- Accepted by the hiring manager from AI output 7. -->\n"
    )


def test_read_drops_every_provenance_line(tmp_path) -> None:
    # A draft that copied an earlier provenance line, accepted again.
    hiring_files.write_job_description(
        tmp_path,
        "ceo",
        "# CEO\n\nText.\n\n<!-- Accepted by the hiring manager from AI output 1. -->",
        ai_output_id=2,
    )

    assert hiring_files.read_job_description(tmp_path, "ceo") == "# CEO\n\nText.\n"
