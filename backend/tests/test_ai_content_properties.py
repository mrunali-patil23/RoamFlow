"""
Property-based tests for AI content generation service.
Tests universal properties that should hold for all valid inputs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch, MagicMock
import string

# Configure hypothesis to run fewer examples for faster testing
settings.register_profile("fast", max_examples=10, deadline=2000)
settings.load_profile("fast")

# Feature: ai-trip-planner, Property 8: AI Content Generation Standards
# **Validates: Requirements 4.1, 4.2, 4.3**

# Strategy for generating attraction data
attraction_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=3, max_size=50, alphabet=string.ascii_letters + string.digits + ' '),
    'rating': st.one_of(st.floats(min_value=1.0, max_value=5.0), st.just('N/A')),
    'address': st.text(min_size=5, max_size=100, alphabet=string.ascii_letters + string.digits + ' ,-'),
    'type': st.sampled_from(['Museum', 'Park', 'Monument', 'Temple', 'Beach', 'Market', 'Gallery'])
})

# Strategy for generating hotel data
hotel_strategy = st.fixed_dictionaries({
    'name': st.text(min_size=3, max_size=50, alphabet=string.ascii_letters + string.digits + ' '),
    'overall_rating': st.one_of(st.floats(min_value=1.0, max_value=5.0), st.just('N/A')),
    'rate_per_night': st.fixed_dictionaries({
        'lowest': st.one_of(st.floats(min_value=500, max_value=50000), st.just('N/A'))
    }),
    'amenities': st.lists(st.sampled_from(['WiFi', 'Pool', 'Gym', 'Spa', 'Restaurant', 'Bar', 'Parking']), max_size=5),
    'neighborhood': st.text(min_size=3, max_size=30, alphabet=string.ascii_letters + ' ')
})

# Strategy for generating event data
event_strategy = st.fixed_dictionaries({
    'title': st.text(min_size=3, max_size=50, alphabet=string.ascii_letters + string.digits + ' '),
    'date': st.fixed_dictionaries({
        'start_date': st.sampled_from(['2024-03-15', '2024-04-20', '2024-05-10', 'TBD'])
    }),
    'venue': st.fixed_dictionaries({
        'name': st.text(min_size=3, max_size=40, alphabet=string.ascii_letters + ' ')
    }),
    'event_category': st.sampled_from(['Concert', 'Festival', 'Exhibition', 'Sports', 'Theater', 'Conference']),
    'description': st.text(min_size=10, max_size=200, alphabet=string.ascii_letters + string.digits + ' .,!')
})

@given(attraction=attraction_strategy)
def test_property_attraction_description_standards(attraction):
    """
    Property 8: AI Content Generation Standards (Attractions)
    For any travel item (attraction), the Gemini API should generate descriptions 
    that are 2-3 lines in length and contextually relevant.
    **Validates: Requirements 4.1**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with valid description
        mock_response = Mock()
        mock_response.text = f"This is a wonderful {attraction.get('type', 'attraction')} located in the heart of the city. Visitors can enjoy the unique atmosphere and rich cultural experience. It's highly rated and offers great value for tourists."
        mock_model.generate_content.return_value = mock_response
        
        # Import and create service
        from ai_content_service import AIContentService
        
        service = AIContentService()
        description = service.generate_attraction_description(attraction)
        
        # Property: Description should be a non-empty string
        assert isinstance(description, str), f"Description should be string: {type(description)}"
        assert len(description.strip()) > 0, "Description should not be empty"
        
        # Property: Description should be reasonable length (2-3 lines, roughly 50-300 characters)
        assert 20 <= len(description) <= 500, f"Description length should be reasonable: {len(description)} chars"
        
        # Property: Description should contain relevant information
        attraction_name = attraction.get('title', '').strip()
        if attraction_name and len(attraction_name) > 2:
            # Either the name should appear or the type should be referenced
            name_mentioned = attraction_name.lower() in description.lower()
            type_mentioned = attraction.get('type', '').lower() in description.lower()
            assert name_mentioned or type_mentioned or 'attraction' in description.lower(), \
                f"Description should reference the attraction: {description}"
        
        # Property: Description should not contain placeholder text
        placeholder_words = ['lorem', 'ipsum', 'placeholder', 'example', 'sample']
        description_lower = description.lower()
        for word in placeholder_words:
            assert word not in description_lower, f"Description should not contain placeholder text: {word}"
        
        # Property: Description should be properly formatted (no excessive whitespace)
        assert description == description.strip(), "Description should not have leading/trailing whitespace"
        assert '  ' not in description, "Description should not have double spaces"

@given(hotel=hotel_strategy)
def test_property_hotel_description_standards(hotel):
    """
    Property 8: AI Content Generation Standards (Hotels)
    For any travel item (hotel), the Gemini API should generate descriptions 
    that are 2-3 lines in length and contextually relevant.
    **Validates: Requirements 4.2**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with valid description
        mock_response = Mock()
        mock_response.text = f"This comfortable hotel offers excellent amenities and service. Located in a convenient area with easy access to attractions. Guests appreciate the quality accommodations and friendly staff."
        mock_model.generate_content.return_value = mock_response
        
        # Import and create service
        from ai_content_service import AIContentService
        
        service = AIContentService()
        description = service.generate_hotel_description(hotel)
        
        # Property: Description should be a non-empty string
        assert isinstance(description, str), f"Description should be string: {type(description)}"
        assert len(description.strip()) > 0, "Description should not be empty"
        
        # Property: Description should be reasonable length (2-3 lines, roughly 50-300 characters)
        assert 20 <= len(description) <= 500, f"Description length should be reasonable: {len(description)} chars"
        
        # Property: Description should contain hotel-related terms
        hotel_terms = ['hotel', 'accommodation', 'room', 'guest', 'stay', 'service', 'amenities', 'comfort']
        description_lower = description.lower()
        has_hotel_term = any(term in description_lower for term in hotel_terms)
        assert has_hotel_term, f"Description should contain hotel-related terms: {description}"
        
        # Property: Description should reference hotel name if provided
        hotel_name = hotel.get('name', '').strip()
        if hotel_name and len(hotel_name) > 2 and hotel_name != 'Unknown Hotel':
            name_mentioned = hotel_name.lower() in description.lower()
            # Allow for partial name matching or generic hotel references
            assert name_mentioned or 'hotel' in description_lower, \
                f"Description should reference the hotel: {description}"
        
        # Property: Description should not contain placeholder text
        placeholder_words = ['lorem', 'ipsum', 'placeholder', 'example', 'sample']
        for word in placeholder_words:
            assert word not in description_lower, f"Description should not contain placeholder text: {word}"
        
        # Property: Description should be properly formatted
        assert description == description.strip(), "Description should not have leading/trailing whitespace"
        assert '  ' not in description, "Description should not have double spaces"

@given(event=event_strategy)
def test_property_event_description_standards(event):
    """
    Property 8: AI Content Generation Standards (Events)
    For any travel item (event), the Gemini API should generate descriptions 
    that are 2-3 lines in length and contextually relevant.
    **Validates: Requirements 4.3**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with valid description
        mock_response = Mock()
        event_type = event.get('event_category', 'event')
        mock_response.text = f"This exciting {event_type.lower()} offers visitors a unique cultural experience. Attendees can enjoy entertainment and immerse themselves in local traditions. It's a must-see event for travelers seeking authentic experiences."
        mock_model.generate_content.return_value = mock_response
        
        # Import and create service
        from ai_content_service import AIContentService
        
        service = AIContentService()
        description = service.generate_event_description(event)
        
        # Property: Description should be a non-empty string
        assert isinstance(description, str), f"Description should be string: {type(description)}"
        assert len(description.strip()) > 0, "Description should not be empty"
        
        # Property: Description should be reasonable length (2-3 lines, roughly 50-300 characters)
        assert 20 <= len(description) <= 500, f"Description length should be reasonable: {len(description)} chars"
        
        # Property: Description should contain event-related terms
        event_terms = ['event', 'experience', 'attend', 'visitor', 'cultural', 'entertainment', 'celebration']
        description_lower = description.lower()
        has_event_term = any(term in description_lower for term in event_terms)
        assert has_event_term, f"Description should contain event-related terms: {description}"
        
        # Property: Description should reference event category if provided
        event_category = event.get('event_category', '').strip()
        if event_category and len(event_category) > 2:
            category_mentioned = event_category.lower() in description_lower
            # Allow for generic event references
            assert category_mentioned or 'event' in description_lower, \
                f"Description should reference the event category: {description}"
        
        # Property: Description should not contain placeholder text
        placeholder_words = ['lorem', 'ipsum', 'placeholder', 'example', 'sample']
        for word in placeholder_words:
            assert word not in description_lower, f"Description should not contain placeholder text: {word}"
        
        # Property: Description should be properly formatted
        assert description == description.strip(), "Description should not have leading/trailing whitespace"
        assert '  ' not in description, "Description should not have double spaces"

# Feature: ai-trip-planner, Property 9: Conditional AI Content Generation
# **Validates: Requirements 4.4, 4.5**

# Strategy for generating weather data
weather_strategy = st.fixed_dictionaries({
    'temperature': st.one_of(st.integers(min_value=-10, max_value=50), st.just('N/A')),
    'weather': st.sampled_from(['Sunny', 'Rainy', 'Cloudy', 'Stormy', 'Snowy', 'Foggy']),
    'humidity': st.one_of(st.integers(min_value=10, max_value=100), st.just('N/A')),
    'precipitation': st.floats(min_value=0.0, max_value=100.0)
})

# Strategy for generating budget status
budget_status_strategy = st.fixed_dictionaries({
    'status': st.sampled_from(['Within Budget', 'Slightly Over Budget', 'Over Budget']),
    'difference_inr': st.floats(min_value=-10000.0, max_value=50000.0),
    'max_budget_inr': st.floats(min_value=10000.0, max_value=100000.0),
    'total_cost_inr': st.floats(min_value=15000.0, max_value=150000.0)
})

@given(
    weather_data=weather_strategy,
    destination=st.text(min_size=3, max_size=30, alphabet=string.ascii_letters + ' ')
)
def test_property_weather_travel_tips_generation(weather_data, destination):
    """
    Property 9: Conditional AI Content Generation (Weather Tips)
    For any trip plan with weather data, the Gemini API should generate 
    appropriate tips when conditions are met.
    **Validates: Requirements 4.4**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with weather-appropriate tips
        weather_condition = weather_data.get('weather', 'Unknown')
        mock_response = Mock()
        mock_response.text = f"Based on the {weather_condition.lower()} weather conditions in {destination}, pack appropriate clothing and plan indoor alternatives. Consider waterproof gear if rain is expected. Check local weather updates before outdoor activities."
        mock_model.generate_content.return_value = mock_response
        
        # Import and create service
        from ai_content_service import AIContentService
        
        service = AIContentService()
        tips = service.generate_weather_travel_tips(weather_data, destination)
        
        # Property: Tips should be a non-empty string
        assert isinstance(tips, str), f"Tips should be string: {type(tips)}"
        assert len(tips.strip()) > 0, "Tips should not be empty"
        
        # Property: Tips should be reasonable length
        assert 20 <= len(tips) <= 1000, f"Tips length should be reasonable: {len(tips)} chars"
        
        # Property: Tips should reference the destination
        destination_clean = destination.strip()
        if destination_clean and len(destination_clean) > 2:
            assert destination_clean.lower() in tips.lower(), \
                f"Tips should reference the destination: {destination_clean} not in {tips}"
        
        # Property: Tips should contain weather-related advice
        weather_terms = ['weather', 'temperature', 'rain', 'sun', 'pack', 'clothing', 'outdoor', 'indoor']
        tips_lower = tips.lower()
        has_weather_term = any(term in tips_lower for term in weather_terms)
        assert has_weather_term, f"Tips should contain weather-related advice: {tips}"
        
        # Property: Tips should be actionable (contain action words)
        action_words = ['pack', 'bring', 'wear', 'consider', 'check', 'plan', 'avoid', 'prepare']
        has_action_word = any(word in tips_lower for word in action_words)
        assert has_action_word, f"Tips should be actionable: {tips}"
        
        # Property: Tips should not contain placeholder text
        placeholder_words = ['lorem', 'ipsum', 'placeholder', 'example', 'sample']
        for word in placeholder_words:
            assert word not in tips_lower, f"Tips should not contain placeholder text: {word}"
        
        # Property: Tips should be properly formatted
        assert tips == tips.strip(), "Tips should not have leading/trailing whitespace"

@given(budget_status_data=budget_status_strategy)
def test_property_cost_saving_advice_generation(budget_status_data):
    """
    Property 9: Conditional AI Content Generation (Cost-Saving Advice)
    For any trip plan where budget constraints are detected, the Gemini API 
    should suggest cost-saving advice when conditions are met.
    **Validates: Requirements 4.5**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Mock response with cost-saving suggestions
        mock_response = Mock()
        mock_response.text = """Consider staying in budget accommodations instead of luxury hotels.
Book flights in advance for better prices.
Choose local restaurants over tourist establishments.
Use public transportation instead of taxis.
Look for free attractions and activities."""
        mock_model.generate_content.return_value = mock_response
        
        # Import and create service
        from ai_content_service import AIContentService, BudgetStatus
        
        # Create BudgetStatus object
        budget_status = BudgetStatus(
            status=budget_status_data['status'],
            difference_inr=budget_status_data['difference_inr'],
            max_budget_inr=budget_status_data['max_budget_inr'],
            total_cost_inr=budget_status_data['total_cost_inr']
        )
        
        service = AIContentService()
        advice = service.generate_cost_saving_advice(budget_status)
        
        # Property: Advice should be a list of strings
        assert isinstance(advice, list), f"Advice should be list: {type(advice)}"
        assert len(advice) > 0, "Advice should not be empty"
        
        # Property: Each advice item should be a non-empty string
        for item in advice:
            assert isinstance(item, str), f"Each advice item should be string: {type(item)}"
            assert len(item.strip()) > 0, "Each advice item should not be empty"
            assert len(item) >= 10, f"Each advice item should be substantial: {len(item)} chars"
        
        # Property: Advice should contain cost-related terms
        cost_terms = ['budget', 'cheap', 'save', 'cost', 'price', 'money', 'affordable', 'discount', 'free']
        advice_text = ' '.join(advice).lower()
        has_cost_term = any(term in advice_text for term in cost_terms)
        assert has_cost_term, f"Advice should contain cost-related terms: {advice}"
        
        # Property: Advice should be actionable (contain action words)
        action_words = ['consider', 'choose', 'book', 'use', 'look', 'stay', 'eat', 'travel', 'find']
        has_action_word = any(word in advice_text for word in action_words)
        assert has_action_word, f"Advice should be actionable: {advice}"
        
        # Property: Advice should cover different expense categories
        expense_categories = ['accommodation', 'hotel', 'flight', 'transport', 'food', 'restaurant', 'attraction', 'activity']
        categories_mentioned = sum(1 for category in expense_categories if category in advice_text)
        assert categories_mentioned >= 2, f"Advice should cover multiple expense categories: {advice}"
        
        # Property: Advice should not contain placeholder text
        placeholder_words = ['lorem', 'ipsum', 'placeholder', 'example', 'sample']
        for word in placeholder_words:
            assert word not in advice_text, f"Advice should not contain placeholder text: {word}"
        
        # Property: Each advice item should be properly formatted
        for item in advice:
            assert item == item.strip(), f"Advice item should not have leading/trailing whitespace: '{item}'"
        
        # Property: Should provide reasonable number of suggestions (2-5)
        assert 2 <= len(advice) <= 5, f"Should provide 2-5 suggestions: {len(advice)}"

@given(
    weather_data=weather_strategy,
    budget_status_data=budget_status_strategy,
    destination=st.text(min_size=3, max_size=30, alphabet=string.ascii_letters + ' ')
)
def test_property_conditional_content_consistency(weather_data, budget_status_data, destination):
    """
    Property 9: Conditional AI Content Generation (Consistency)
    For any combination of conditions (weather + budget), the system should 
    generate appropriate conditional content consistently.
    **Validates: Requirements 4.4, 4.5**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model with different responses for different prompts
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        def mock_generate_content(prompt, generation_config=None):
            mock_response = Mock()
            if 'weather' in prompt.lower():
                mock_response.text = f"Weather-based travel tips for {destination}: Pack appropriate clothing and check conditions regularly."
            elif 'budget' in prompt.lower() or 'cost' in prompt.lower():
                mock_response.text = "Consider budget accommodations.\nBook flights early.\nUse public transport.\nEat at local places."
            else:
                mock_response.text = "General travel advice for your trip."
            return mock_response
        
        mock_model.generate_content.side_effect = mock_generate_content
        
        # Import and create service
        from ai_content_service import AIContentService, BudgetStatus
        
        service = AIContentService()
        
        # Generate weather tips
        weather_tips = service.generate_weather_travel_tips(weather_data, destination)
        
        # Generate cost-saving advice
        budget_status = BudgetStatus(
            status=budget_status_data['status'],
            difference_inr=budget_status_data['difference_inr'],
            max_budget_inr=budget_status_data['max_budget_inr'],
            total_cost_inr=budget_status_data['total_cost_inr']
        )
        cost_advice = service.generate_cost_saving_advice(budget_status)
        
        # Property: Both types of content should be generated
        assert isinstance(weather_tips, str), "Weather tips should be string"
        assert isinstance(cost_advice, list), "Cost advice should be list"
        assert len(weather_tips.strip()) > 0, "Weather tips should not be empty"
        assert len(cost_advice) > 0, "Cost advice should not be empty"
        
        # Property: Content should be contextually different
        weather_tips_lower = weather_tips.lower()
        cost_advice_text = ' '.join(cost_advice).lower()
        
        # Weather tips should focus on weather-related advice
        weather_focus_terms = ['weather', 'temperature', 'rain', 'clothing', 'pack']
        weather_has_focus = any(term in weather_tips_lower for term in weather_focus_terms)
        assert weather_has_focus, f"Weather tips should focus on weather: {weather_tips}"
        
        # Cost advice should focus on budget-related advice
        cost_focus_terms = ['budget', 'cost', 'save', 'cheap', 'price', 'money']
        cost_has_focus = any(term in cost_advice_text for term in cost_focus_terms)
        assert cost_has_focus, f"Cost advice should focus on budget: {cost_advice}"
        
        # Property: Content should not overlap significantly
        # (They should address different aspects of travel planning)
        weather_words = set(weather_tips_lower.split())
        cost_words = set(cost_advice_text.split())
        overlap = weather_words.intersection(cost_words)
        # Allow some common words but not too much overlap
        common_words = {'the', 'and', 'or', 'to', 'for', 'in', 'on', 'at', 'with', 'your', 'travel', 'trip'}
        significant_overlap = overlap - common_words
        overlap_ratio = len(significant_overlap) / max(len(weather_words), len(cost_words), 1)
        assert overlap_ratio < 0.5, f"Content should not overlap significantly: {overlap_ratio}"
        
        # Property: Both should be properly formatted
        assert weather_tips == weather_tips.strip(), "Weather tips should be properly formatted"
        for advice_item in cost_advice:
            assert advice_item == advice_item.strip(), f"Cost advice should be properly formatted: '{advice_item}'"
# Feature: ai-trip-planner, Property 10: API Responsibility Separation
# **Validates: Requirements 4.6**

@given(
    attraction=attraction_strategy,
    hotel=hotel_strategy,
    event=event_strategy,
    weather_data=weather_strategy,
    budget_status_data=budget_status_strategy
)
def test_property_api_responsibility_separation(attraction, hotel, event, weather_data, budget_status_data):
    """
    Property 10: API Responsibility Separation
    For any Gemini API call, the request should only contain content generation 
    parameters and never include data fetching operations.
    **Validates: Requirements 4.6**
    """
    # Mock the Gemini API to capture all calls
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model to capture all generate_content calls
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        # Track all API calls
        api_calls = []
        
        def mock_generate_content(prompt, generation_config=None):
            # Capture the call details
            api_calls.append({
                'prompt': prompt,
                'generation_config': generation_config
            })
            
            # Return appropriate mock response based on prompt content
            mock_response = Mock()
            if 'attraction' in prompt.lower():
                mock_response.text = "This attraction offers a unique cultural experience for visitors."
            elif 'hotel' in prompt.lower():
                mock_response.text = "This hotel provides comfortable accommodations with modern amenities."
            elif 'event' in prompt.lower():
                mock_response.text = "This event showcases local culture and entertainment."
            elif 'weather' in prompt.lower():
                mock_response.text = "Pack appropriate clothing and check weather conditions regularly."
            elif 'budget' in prompt.lower() or 'cost' in prompt.lower():
                mock_response.text = "Consider budget accommodations and local transportation options."
            else:
                mock_response.text = "General travel advice for your trip."
            return mock_response
        
        mock_model.generate_content.side_effect = mock_generate_content
        
        # Import and create service
        from ai_content_service import AIContentService, BudgetStatus
        
        service = AIContentService()
        
        # Make various API calls
        service.generate_attraction_description(attraction)
        service.generate_hotel_description(hotel)
        service.generate_event_description(event)
        service.generate_weather_travel_tips(weather_data, "Test Destination")
        
        budget_status = BudgetStatus(
            status=budget_status_data['status'],
            difference_inr=budget_status_data['difference_inr'],
            max_budget_inr=budget_status_data['max_budget_inr'],
            total_cost_inr=budget_status_data['total_cost_inr']
        )
        service.generate_cost_saving_advice(budget_status)
        
        # Property: All calls should be to generate_content (content generation only)
        assert len(api_calls) >= 5, f"Should have made at least 5 API calls: {len(api_calls)}"
        
        # Property: No API calls should contain data fetching operations
        forbidden_data_operations = [
            'fetch', 'retrieve', 'get_data', 'download', 'scrape', 'search_api',
            'serp_api', 'google_flights', 'google_hotels', 'google_maps',
            'api_key', 'http_request', 'url', 'endpoint', 'query_api'
        ]
        
        for call in api_calls:
            prompt = call['prompt'].lower()
            for operation in forbidden_data_operations:
                assert operation not in prompt, \
                    f"Gemini API call should not contain data fetching operation '{operation}': {prompt[:200]}..."
        
        # Property: All calls should be content generation requests
        content_generation_indicators = [
            'generate', 'describe', 'create', 'write', 'provide', 'suggest'
        ]
        
        for call in api_calls:
            prompt = call['prompt'].lower()
            has_content_indicator = any(indicator in prompt for indicator in content_generation_indicators)
            assert has_content_indicator, \
                f"Gemini API call should be for content generation: {prompt[:200]}..."
        
        # Property: All calls should have appropriate generation configuration
        for call in api_calls:
            config = call['generation_config']
            if config:
                # Should contain content generation parameters, not data fetching parameters
                assert 'temperature' in config or 'max_output_tokens' in config, \
                    f"Generation config should contain content parameters: {config}"
                
                # Should not contain data fetching parameters
                forbidden_config_keys = ['api_key', 'endpoint', 'search_query', 'data_source']
                for key in forbidden_config_keys:
                    assert key not in config, \
                        f"Generation config should not contain data fetching parameter '{key}': {config}"
        
        # Property: Prompts should contain input data, not requests for external data
        for call in api_calls:
            prompt = call['prompt']
            
            # Should contain provided data (attraction info, hotel info, etc.)
            # Make case-insensitive by checking both formats
            data_indicators = ['name:', 'title:', 'rating:', 'temperature:', 'budget:', 'status:', 
                             'Name:', 'Title:', 'Rating:', 'Temperature:', 'Budget:', 'Status:',
                             'Location:', 'Type:', 'Date:', 'Venue:', 'Weather:', 'Humidity:']
            has_data_indicator = any(indicator in prompt for indicator in data_indicators)
            assert has_data_indicator, \
                f"Prompt should contain provided data, not request external data: {prompt[:200]}..."
            
            # Should not request external data fetching
            external_requests = [
                'fetch from', 'get from api', 'search for', 'look up', 'retrieve from',
                'call api', 'query database', 'access external'
            ]
            for request in external_requests:
                assert request not in prompt.lower(), \
                    f"Prompt should not request external data: '{request}' in {prompt[:200]}..."
        
        # Property: Each call should be for a specific content type
        content_types = ['attraction', 'hotel', 'event', 'weather', 'budget', 'cost']
        for call in api_calls:
            prompt = call['prompt'].lower()
            matching_types = [content_type for content_type in content_types if content_type in prompt]
            assert len(matching_types) >= 1, \
                f"Each call should be for a specific content type: {prompt[:200]}..."
        
        # Property: No call should try to access multiple data sources
        data_sources = ['serp', 'google', 'api', 'database', 'external', 'web']
        for call in api_calls:
            prompt = call['prompt'].lower()
            mentioned_sources = [source for source in data_sources if source in prompt]
            # Allow mentioning data in context, but not requesting access to sources
            access_words = ['access', 'fetch', 'get', 'retrieve', 'call', 'query']
            for source in mentioned_sources:
                for access_word in access_words:
                    combined = f"{access_word} {source}"
                    assert combined not in prompt, \
                        f"Prompt should not request access to external sources: '{combined}' in {prompt[:200]}..."

@given(
    content_type=st.sampled_from(['attraction', 'hotel', 'event', 'weather', 'budget']),
    data_dict=st.dictionaries(
        st.text(min_size=1, max_size=20, alphabet=string.ascii_letters),
        st.one_of(st.text(min_size=1, max_size=50), st.floats(), st.integers()),
        min_size=1, max_size=5
    )
)
def test_property_gemini_api_content_only_calls(content_type, data_dict):
    """
    Property 10: API Responsibility Separation (Content-Only Calls)
    For any content generation request, the Gemini API should only receive 
    content generation instructions with provided data, never data fetching requests.
    **Validates: Requirements 4.6**
    """
    # Mock the Gemini API
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model_class, \
         patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'}):
        
        # Setup mock model to capture calls
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        captured_calls = []
        
        def capture_generate_content(prompt, generation_config=None):
            captured_calls.append({
                'prompt': prompt,
                'config': generation_config,
                'content_type': content_type
            })
            mock_response = Mock()
            mock_response.text = f"Generated content for {content_type} based on provided data."
            return mock_response
        
        mock_model.generate_content.side_effect = capture_generate_content
        mock_model_class.return_value = mock_model
        
        # Import and create service
        from ai_content_service import AIContentService
        
        service = AIContentService()
        
        # Make a content generation call based on content type
        if content_type == 'attraction':
            service.generate_attraction_description(data_dict)
        elif content_type == 'hotel':
            service.generate_hotel_description(data_dict)
        elif content_type == 'event':
            service.generate_event_description(data_dict)
        elif content_type == 'weather':
            service.generate_weather_travel_tips(data_dict, "Test City")
        elif content_type == 'budget':
            from ai_content_service import BudgetStatus
            budget_status = BudgetStatus(
                status="Over Budget",
                difference_inr=5000.0,
                max_budget_inr=50000.0,
                total_cost_inr=55000.0
            )
            service.generate_cost_saving_advice(budget_status)
        
        # Property: Should have made exactly one API call
        assert len(captured_calls) == 1, f"Should make exactly one API call: {len(captured_calls)}"
        
        call = captured_calls[0]
        prompt = call['prompt']
        
        # Property: Prompt should be a content generation instruction
        generation_verbs = ['generate', 'create', 'write', 'describe', 'provide', 'suggest']
        prompt_lower = prompt.lower()
        has_generation_verb = any(verb in prompt_lower for verb in generation_verbs)
        assert has_generation_verb, f"Prompt should contain content generation instruction: {prompt[:100]}..."
        
        # Property: Prompt should contain the provided data
        # For structured data types, check if the prompt contains the expected structure
        # For arbitrary data dict, check if any key or value appears
        data_mentioned = False
        if content_type in ['attraction', 'hotel', 'event']:
            # For structured content types, check for standard fields
            standard_fields = ['name', 'title', 'rating', 'type', 'location', 'venue', 'category']
            for field in standard_fields:
                if field.lower() in prompt_lower:
                    data_mentioned = True
                    break
        else:
            # For other types, check if any provided data appears
            for key, value in data_dict.items():
                if str(key).lower() in prompt_lower or str(value).lower() in prompt_lower:
                    data_mentioned = True
                    break
        
        # If no data mentioned yet, check if the prompt contains any data structure indicators
        if not data_mentioned:
            data_structure_indicators = [':', 'name', 'title', 'rating', 'temperature', 'budget', 'status']
            data_mentioned = any(indicator in prompt_lower for indicator in data_structure_indicators)
        
        assert data_mentioned, f"Prompt should reference provided data: {prompt[:100]}..."
        
        # Property: Prompt should NOT contain data fetching instructions
        fetching_verbs = ['fetch', 'retrieve', 'get', 'download', 'scrape', 'search', 'query', 'access']
        for verb in fetching_verbs:
            # Allow these words in context (e.g., "get content" is OK, "get from API" is not)
            forbidden_phrases = [f"{verb} from", f"{verb} data", f"{verb} information"]
            for phrase in forbidden_phrases:
                assert phrase not in prompt_lower, \
                    f"Prompt should not contain data fetching instruction '{phrase}': {prompt[:100]}..."
        
        # Property: Prompt should NOT reference external APIs or services
        external_services = ['serp_api', 'google_api', 'api_key', 'external_service', 'web_service']
        for service_name in external_services:
            assert service_name not in prompt_lower, \
                f"Prompt should not reference external service '{service_name}': {prompt[:100]}..."
        
        # Property: Generation config should be for content generation only
        config = call['config']
        if config:
            # Should have content generation parameters
            content_params = ['temperature', 'max_output_tokens', 'top_p', 'top_k']
            has_content_param = any(param in config for param in content_params)
            assert has_content_param, f"Config should have content generation parameters: {config}"
            
            # Should NOT have data fetching parameters
            data_params = ['api_key', 'endpoint', 'search_query', 'data_source', 'url']
            for param in data_params:
                assert param not in config, \
                    f"Config should not have data fetching parameter '{param}': {config}"