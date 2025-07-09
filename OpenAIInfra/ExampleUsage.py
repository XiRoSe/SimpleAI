"""
SimpleAI Usage Examples
Demonstrates how to use all components of the SimpleAI library.
"""

import logging
from configs import ChatConfig, VisionConfig
from chat_gpt import ChatGPT
from vision_gpt import VisionGPT
from local_chat_memory import ChatMemory


# Set up logging
logging.basicConfig(level=logging.INFO)


def main():
    print("=== SimpleAI Examples ===\n")

    # Example 1: Basic Chat (API key loaded from .env automatically)
    print("1. Basic Chat Example (using .env)")
    config = ChatConfig(
        model="gpt-4o-mini",
        temperature=0.7,
        memory_size=10
    )

    chat = ChatGPT(config)
    response = chat.chat("Hello! What's the weather like today?")
    print(f"Response: {response}\n")

    # Show memory stats
    stats = chat.get_memory_stats()
    print(f"Memory stats: {stats}\n")

    # Example 2: Different Chat Methods
    print("2. Different Chat Methods")

    # Simple completion
    completion = chat.complete("Write a song about programming")
    print(f"Haiku: {completion}\n")

    # Question without memory
    answer = chat.ask("What is Python?")
    print(f"Python explanation: {answer}\n")

    # Role playing
    shakespeare = chat.role_play("Shakespeare", "Tell me about love")
    print(f"Shakespeare: {shakespeare}\n")

    # Example 3: Utility Functions
    print("3. Utility Functions")

    # Summarization
    long_text = """
    Artificial Intelligence (AI) refers to the simulation of human intelligence in machines 
    that are programmed to think like humans and mimic their actions. The term may also be 
    applied to any machine that exhibits traits associated with a human mind such as learning 
    and problem-solving. AI has applications in various fields including healthcare, finance, 
    transportation, and entertainment.
    """

    summary = chat.summarize(long_text, style="bullet")
    print(f"Summary: {summary}\n")

    # Translation
    translation = chat.translate("Hello, how are you?", "Spanish")
    print(f"Translation: {translation}\n")

    # Example 4: Vision Analysis (if working image URL available)
    print("4. Vision Analysis Example")
    try:
        vision_config = VisionConfig(detail="auto")  # API key auto-loaded
        vision = VisionGPT(vision_config)

        # Use a reliable test image
        test_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

        # Validate URL first
        validation = vision.validate_image_url(test_image)
        print(f"URL validation: {validation}")

        if validation["is_vision_compatible"]:
            description = vision.describe_scene(test_image)
            print(f"Scene description: {description}\n")

            objects = vision.identify_objects(test_image)
            print(f"Objects identified: {objects}\n")
        else:
            print("Test image URL not compatible with Vision API\n")

    except Exception as e:
        print(f"Vision analysis failed: {e}\n")

    # Example 5: Memory Management
    print("5. Memory Management Example")

    memory = ChatMemory(max_length=5)

    # Add some messages
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")
    memory.add_message("user", "How are you?")
    memory.add_message("assistant", "I'm doing well, thank you!")

    print(f"Messages in memory: {len(memory.get_messages())}")
    print(f"Memory stats: {memory.get_memory_stats()}")

    # Get messages by role
    user_messages = memory.get_messages_by_role("user")
    print(f"User messages: {len(user_messages)}")

    # Example 6: Configuration Examples
    print("\n6. Different Configurations")

    # High creativity config
    creative_config = ChatConfig(
        model="gpt-4o-mini",
        temperature=1.5,  # More creative
        max_tokens=200,
        memory_size=20
    )

    creative_chat = ChatGPT(creative_config)
    creative_response = creative_chat.complete("Write a creative story opening")
    print(f"Creative response: {creative_response}\n")

    # Conservative config
    conservative_config = ChatConfig(
        model="gpt-4o-mini",
        temperature=0.1,  # More focused
        max_tokens=100,
        memory_size=5
    )

    conservative_chat = ChatGPT(conservative_config)
    conservative_response = conservative_chat.complete("Explain machine learning")
    print(f"Conservative response: {conservative_response}\n")

    # Example 7: Save and Load Conversation
    print("7. Save/Load Conversation")

    try:
        # Save current conversation
        chat.save_conversation("example_conversation.json")
        print("Conversation saved to example_conversation.json")

        # Create new chat and load conversation
        new_chat = ChatGPT(config)
        new_chat.load_conversation("example_conversation.json")
        print(f"Loaded conversation with {len(new_chat.memory.get_messages())} messages")

    except Exception as e:
        print(f"Save/load failed: {e}")

    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    main()