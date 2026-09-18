import json
import sys
from pathlib import Path

from module2.pipeline import run_validation


DEFAULT_INPUT_FILE = Path(__file__).parent / "test_input.json"


def load_input_file(file_path: Path) -> dict:
    """Load mock Module-1 output from a JSON file."""

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        print(f"\nERROR: Input file not found:")
        print(f"  {file_path}")
        sys.exit(1)

    except json.JSONDecodeError as error:
        print("\nERROR: Invalid JSON file.")
        print(f"  Line: {error.lineno}")
        print(f"  Column: {error.colno}")
        print(f"  Message: {error.msg}")
        sys.exit(1)

    if not isinstance(data, dict):
        print("\nERROR: JSON root must be an object.")
        sys.exit(1)

    return data


def print_result(result: dict) -> None:
    """Print validation result in readable JSON format."""

    def serialize(value):
        # Handle Enum values such as CheckStatus.PASS
        if hasattr(value, "value") and not isinstance(
            value,
            (str, int, float, bool)
        ):
            return value.value

        # Handle dataclasses such as ValidationCheck
        if hasattr(value, "__dataclass_fields__"):
            return {
                field_name: serialize(getattr(value, field_name))
                for field_name in value.__dataclass_fields__
            }

        # Handle dictionaries
        if isinstance(value, dict):
            return {
                key: serialize(item)
                for key, item in value.items()
            }

        # Handle lists and tuples
        if isinstance(value, (list, tuple)):
            return [
                serialize(item)
                for item in value
            ]

        return value

    print("\n" + "=" * 70)
    print("MODULE 2 VALIDATION RESULT")
    print("=" * 70)

    print(
        json.dumps(
            serialize(result),
            indent=2,
            ensure_ascii=False
        )
    )

    print("=" * 70)



def main() -> None:
    # Allow an optional JSON file from the command line.
    #
    # Example:
    # python -m module2.manual_test
    #
    # Or:
    # python -m module2.manual_test some_test.json

    if len(sys.argv) > 2:
        print("Usage:")
        print("  python -m module2.manual_test")
        print("  python -m module2.manual_test <json_file>")
        sys.exit(1)

    if len(sys.argv) == 2:
        input_file = Path(sys.argv[1])

        # If a relative path is supplied, interpret it relative
        # to the current working directory.
        if not input_file.is_absolute():
            input_file = Path.cwd() / input_file
    else:
        input_file = DEFAULT_INPUT_FILE

    print("\n" + "=" * 70)
    print("MODULE 2 MANUAL TEST")
    print("=" * 70)
    print(f"Input file: {input_file}")

    input_data = load_input_file(input_file)

    document_type = str(
        input_data.get("document_type", "")
    ).upper()

    if not document_type:
        print("\nERROR: 'document_type' is missing from the input.")
        sys.exit(1)

    print(f"Document type: {document_type}")

    # ---------------------------------------------------------
    # Optional passport reference for VISA validation.
    #
    # This allows us to manually test cross-document checks
    # before Module 1 is available.
    #
    # Example:
    #
    # "passport_data": {
    #     "passport_number": "P1234567",
    #     "name": "DOE<<JOHN",
    #     "nationality": "IND",
    #     "expiry_date": "2030-05-19"
    # }
    #
    # passport_data is NOT part of the actual VISA document
    # data. It is only a temporary testing helper.
    # ---------------------------------------------------------

    passport_data = input_data.get("passport_data")

    if passport_data is not None:
        if not isinstance(passport_data, dict):
            print(
                "\nERROR: 'passport_data' must be a JSON object."
            )
            sys.exit(1)

        print("Passport reference: PROVIDED")

    # Do not send the testing-only passport_data field as part
    # of the actual document data.
    validation_input = dict(input_data)
    validation_input.pop("passport_data", None)

    # Send everything through the real Module 2 pipeline.
    result = run_validation(
        validation_input,
        passport_data
    )

    print_result(result)


if __name__ == "__main__":
    main()