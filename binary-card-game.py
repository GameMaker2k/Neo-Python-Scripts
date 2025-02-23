import time  # For optional delays

def generate_cards(num_cards, max_limit=60):
    """Generates number cards using binary logic."""
    max_number = min((1 << num_cards) - 1, max_limit)
    cards = {i + 1: [] for i in range(num_cards)}

    for number in range(1, max_number + 1):
        for card in range(num_cards):
            if number & (1 << card):
                cards[card + 1].append(number)

    return cards

def print_cards(cards, output_format="table"):
    """Prints cards in a formatted table or list format."""
    if output_format == "table":
        print("\n=== Number Cards in Table Format ===")
        card_keys = sorted(cards.keys())
        max_length = max(len(numbers) for numbers in cards.values())

        # Determine column widths dynamically
        column_widths = [max(len(str(num)) for num in cards[card]) for card in card_keys]
        column_widths = [max(w, len("C{}".format(card))) for w, card in zip(column_widths, card_keys)]

        # Print header
        header = "Card  | " + " | ".join("C{}".format(card).rjust(column_widths[i]) for i, card in enumerate(card_keys))
        print(header)
        print("-" * len(header))

        # Print row-wise numbers
        for i in range(max_length):
            row = []
            for j, card in enumerate(card_keys):
                row.append(str(cards[card][i]).rjust(column_widths[j]) if i < len(cards[card]) else " " * column_widths[j])
            print("{:>5} | ".format(i + 1) + " | ".join(row))

    elif output_format == "list":
        print("\n=== Number Cards in List Format ===")
        for card, numbers in cards.items():
            print("Card {}: {}".format(card, numbers))

    else:
        print("Invalid output format. Use 'table' or 'list'.")

def print_single_card(card_number, numbers, output_format="table"):
    """Prints a single card during the guessing phase in table or list format."""
    if output_format == "table":
        print("\n=== Card {} in Table Format ===".format(card_number))
        
        # Determine column width dynamically
        max_num_width = max(len(str(num)) for num in numbers)
        col_width = max(max_num_width, len("Number"))

        # Print header
        print("Idx  | Number".ljust(col_width + 7))
        print("-" * (col_width + 7))

        # Print numbers in table format
        for i, num in enumerate(numbers, 1):
            print("{:>4} | {}".format(i, str(num).rjust(col_width)))

    elif output_format == "list":
        print("\n=== Card {} in List Format ===".format(card_number))
        print("Card {}: {}".format(card_number, numbers))

    else:
        print("Invalid output format. Use 'table' or 'list'.")

def guess_number(cards, output_format="list", delay=False):
    """Interactive guessing function that prompts for user input."""
    print("\n=== Welcome to the Number Guessing Game! ===")
    print("Think of a number between 1 and {}.".format(max(cards[max(cards.keys())])))
    print("I will ask if your number appears on certain cards, and I'll guess your number!\n")

    # Print all cards together at the start in table format (if selected)
    if output_format == "table":
        print_cards(cards, output_format)

    while True:
        guessed_number = 0  # Reset guessed number

        # Loop through each card and prompt the user
        for card, numbers in sorted(cards.items()):
            print("\nChecking Card {}...".format(card))
            if delay:
                time.sleep(1)  # Add delay for interactive effect
            
            # Show single card using correct format
            print_single_card(card, numbers, output_format)

            # Python 2 & 3 compatibility
            try:
                response = raw_input("\nIs your number on this card? (yes/no): ").strip().lower()
            except NameError:
                response = input("\nIs your number on this card? (yes/no): ").strip().lower()

            if response in ["yes", "y"]:
                guessed_number += numbers[0]

        # Reveal the guessed number
        print("\nAnalyzing your responses...")
        if delay:
            time.sleep(1.5)

        print("\n=== Your number is: {} ===".format(guessed_number))

        # Ask if they want to play again
        try:
            again = raw_input("\nWould you like to try again? (yes/no): ").strip().lower()
        except NameError:
            again = input("\nWould you like to try again? (yes/no): ").strip().lower()

        if again not in ["yes", "y"]:
            print("\nThanks for playing! Goodbye!")
            break

# Run the game only if this script is executed directly
if __name__ == "__main__":
    try:
        num_cards = int(input("Enter the number of cards to use (default 6): ") or 6)
        max_limit = int(input("Enter the maximum number to guess (default 60): ") or 60)
    except ValueError:
        num_cards = 6
        max_limit = 60

    # Ask user for output format
    output_format = input("Choose output format ('table' or 'list', default is 'list'): ").strip().lower()
    if output_format not in ["table", "list"]:
        output_format = "list"

    # Ask if they want delays
    try:
        delay_choice = raw_input("Would you like a slight delay for a more interactive experience? (yes/no, default no): ").strip().lower()
    except NameError:
        delay_choice = input("Would you like a slight delay for a more interactive experience? (yes/no, default no): ").strip().lower()
    delay = delay_choice in ["yes", "y"]

    # Generate cards and start guessing
    cards = generate_cards(num_cards, max_limit)
    guess_number(cards, output_format, delay)
