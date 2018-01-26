# TODO texttospeech mutually exclusive with ssml


class _GoogleIntegration():
    """Represents the data.google object of the _ApiAiResponse.

    The _GoogleIntegration object is not to be rendered as a response but rather
    to extend an existing response to be returned to Api.AI. It contains all the
    data required for communicating with Actions on Google via Api.AI.

    The data is sent to the client in the original form and is not processed by API.AI.

    Note that the contents of this class mirror the Actions API.AI webhook format,
    which closely resembles but is not identical to the Conversation webhook API.ai


    Migration guide - https://developers.google.com/actions/reference/v1/migration#apiai_webhook_protocol_changes
    Webhook Response format - https://developers.google.com/actions/apiai/webhook

    # InputPrompt.FIELDS.rich_initial_prompt
    Relavent Field for RIch Response - https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse
    # ExpectedInput.FIELDS.possible_intents
    Relavent field for SystemIntent - https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse

    V1 info - https://developers.google.com/actions/reference/v1/apiai-webhook

    Sample Responses - https://developers.google.com/actions/assistant/responses

    """

    def __init__(self):
        self.expect_response = True
        self.is_ssml = True
        self.speech = ''

        self.system_intent = {}
        self.rich_response = _RichResponse()
        self.final_response = {}

        self._data = {}

    def simple_response(self, speech, display_text, expect_response):
        self.speech = speech
        self.display_text = display_text
        self.expect_response = expect_response

        self.rich_response.add_simple_response_item(speech, display_text)
        expected_intent = _SystemIntent('TEXT')
        self.system_intent = expected_intent

        return self._load_data()

    def suggestion(self, title):
        self.rich_response.add_suggestion(title)
        # expected_intent = _SystemIntent('TEXT')._load_data()
        # self.system_intent = expected_intent
        return self._load_data()

    def link_out(self, dest, url):
        self.rich_response.add_link_out(dest, url)
        return self._load_data()

    def build_card(self, title=None, subtitle=None, body_text=None, img=None, btns=None, img_options=None):
        card = BasicCard(title, subtitle, body_text, img, btns, img_options)
        self.rich_response.add_basic_card(card)
        return self._load_data()

    def attach_card(self, card):
        self.rich_response.add_basic_card(card)
        return self._load_data()

    def attach_list(self, list_obj):
        expected_intent = _SystemIntent('OPTION')
        expected_intent.set_value_data(list_obj)
        self.system_intent = expected_intent
        return self._load_data()

    def _load_data(self):
        self._data['speech'] = self.speech
        self._data['expectUserResponse'] = self.expect_response
        # The ssml field in a SimpleResponse. IGNORED IN V2
        self._data['isSsml'] = True
        self._data['finalResponse'] = {}

        # optional?
        self._data['noInputPrompts'] = []

        # A RichResponse in an expectedInputs.inputPrompt.richInitialPrompt
        self._data['richResponse'] = self.rich_response._load_data()

        # replaces expectedInputs.possibleIntents
        self._data['systemIntent'] = self.system_intent._load_data()
        return self._data


class Image(object):
    """docstring for Image"""

    def __init__(self, url, descr, height=None, width=None):
        super(Image, self).__init__()
        self.url = url
        self.descr = descr
        self.height = height
        self.width = width

    def _build(self):
        obj = {
            "url": self.url,
            "accessibilityText": self.descr,
            "height": self.width,
            "width": self.height,
        }
        return obj


class Button(object):
    """docstring for Button"""

    def __init__(self, title, url):
        super(Button, self).__init__()
        self.title = title
        self.url = url

    def _build(self):
        obj = {
            "title": self.title,
            "openUrlAction": {
                'url': self.url
            },
        }
        return obj


class BasicCard(object):
    """docstring for BasicCard"""

    def __init__(self, title=None, subtitle=None, body_text=None, img=None, btns=None, img_options=None):
        """Represents a BasicCard UI element object to be included in a RichResponse

        [description]

        Keyword Arguments:
            title {str} -- Overall title of the card. Optional.  (default: {None})
            subtitle {str} -- Card Subtitle (default: {None})
            body_text {str} -- Body text of the card. Supports a limited set of markdown syntax for formatting. Required, unless image is present.  (default: {None})
            img {Image} -- A hero image for the card. The height is fixed to 192dp. Optional. (default: {None})
            btns {Button} -- Currently at most 1 button is supported. Optional.  (default: {None})
            img_options {str} -- Type of image display option. Optional.  (default: {None})

        Raises:
            ValueError -- [description]
        """

        super(BasicCard, self).__init__()
        self.title = title
        self.subtitle = subtitle
        self.body_text = body_text
        self.img = img
        self.btns = btns
        self.img_options = img_options or 'DEFAULT'
        self._data = {}

        if self.img is None and self.body_text is None:
            raise ValueError('Body text or an image must be included in a card')

    def _load_data(self):
        self._data['title'] = self.title
        self._data['subtitle'] = self.subtitle
        self._data['formattedText'] = self.body_text
        self._data['image'] = self.img
        self._data['buttons'] = self.btns
        self._data['imageDisplayOptions'] = self.img_options

        return self._data


class ListItem(object):
    """docstring for ListItem"""

    def __init__(self, arg):
        super(ListItem, self).__init__()
        self.arg = arg


class ListSelect(object):
    """docstring for ListSelect"""

    def __init__(self, title=None, items=None):
        super(ListSelect, self).__init__()
        self.title = title
        self.items = items


class _RichResponse(object):

    def __init__(self):
        self.items = []
        self.suggestions = []
        self.link_out = {}

        self._data = {}

    def _load_data(self):
        self._data['items'] = self.items
        if self.suggestions:
            self._data['suggestions'] = self.suggestions
        if self.link_out:
            self._data['linkOutSuggestion'] = self.link_out
        return self._data

    def add_simple_response_item(self, speech, display_text):
        """Builds a simple response containing speech or text to show the user

        Every _RichResponse requires this type of response as the first item

        This object does not include the ssml field found in the Actions API
        because DialogFlowformats the ssml based off the value of data.google.isSsml
        """

        simple = {'textToSpeech': speech, 'displayText': display_text}
        payload = {'simpleResponse': simple}
        self.items.append(payload)

    def add_basic_card(self, card_obj):
        card = {'basicCard': card_obj._load_data()}
        self.items.append(card)

    def add_suggestion(self, title):
        """Provides a suggestion chip that the user can tap to quickly post a reply to the conversation

            If used in a FinalResponse, they will be ignored.
        """
        suggestion = {'title': title}
        self.suggestions.append(suggestion)

    def add_link_out(self, dest, url):
        """An additional suggestion chip that can link out to the associated app or site."""
        if len(self.link_out) > 0:
            raise ValueError('Only one linkOutSuggestion may be given')

        payload = {
            'destinationName': dest,
            'url': url
        }
        self.link_out = payload


SYSTEM_INTENT_TYPES = {
    'actions.intent.TEXT': None,
    'actions.intent.OPTION': 'type.googleapis.com/google.actions.v2.OptionValueSpec'
}


class _SystemIntent(object):
    """Defines expected (Actions) intent along with extra config data

        This represents the type of data to be received from the user.

        To have the Google Assistant just return the raw user input,
        the app should ask for the actions.intent.TEXT intent.

        Possible intents:
            TEXT
            OPTION
            CONFIRMATION
            TRANSACTION_REQUIREMENTS_CHECK
            DELIVERY_ADDRESS
            TRANSACTION_DECISION

        https://developers.google.com/actions/components/intents
        https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse#ExpectedIntent
    """

    def __init__(self, intent='text'):

        self.intent = 'actions.intent.{}'.format(intent.upper())

        self.value_spec_type = SYSTEM_INTENT_TYPES[self.intent]
        self.input_value_data = {}

    def set_value_data(self, value_spec):
        """Attach the conifguration data required by one of the possible intents


        actions.intent.OPTION requires a SimpleSelect, ListSelect, or CarouselSelect value spec object


        Arguments:
            value_spec {obj} -- COnfiguration data for the built-in actions intent
        """
        print('*****')
        print('Setting value spec')
        self.input_value_data['@type'] = self.value_spec_type

        # now just attach the valuespec payload (list/carousel)
        value_spec_data = value_spec._load_data()
        self.input_value_data.update(value_spec_data)
        print('Value data')
        print(self.input_value_data)

    def _load_data(self):
        if self.input_value_data is None:
            return {'intent': self.intent}
        return {'intent': self.intent, 'data': self.input_value_data}


### OptionValueSpec Types ##

class SimpleOption(object):
    """docstring for SelectionItem"""

    def __init__(self, key, title, synonyms=None):
        super(OptionItem, self).__init__()
        self.title. title
        self.key = key
        self.synonyms = synonyms

    def _load_data(self):
        self._data['optionInfo'] = {
            'key': self.key,
            'synonyms': self.synonyms
        }
        if self.title:
            self._data['title'] = title
        return self._data

    def add_synonym(self, syn):
        self._data['synonyms'].appened(syn)


class ListItem(object):
    """docstring for ListItem"""

    def __init__(self, title, synonyms=None, descr=None, image=None):
        super(ListItem, self).__init__()

        self.title = title
        self.synonyms = synonyms
        self.descr = descr
        self.image = image
        self._data = {}

        # docs for title and key both state they are sent to user
        # so use the same value until usage is clear
        self.option_info = {
            'key': self.title,
            'synonyms': self.synonyms
        }

    def _load_data(self):
        self._data['optionInfo'] = self.option_info
        self._data['title'] = self.title
        self._data['description'] = self.descr
        self._data['image'] = self.image
        return self._data


class ListSelect(object):
    """docstring for ListSelect"""

    def __init__(self, title=None, list_items=None):
        super(ListSelect, self).__init__()
        self.title = title
        self.list_items = list_items or []
        self._data = {}

    def attach_item(self, list_item):
        item_data = list_item._load_data()
        self.list_items.append(item_data)

    def add_item(self, title, synonyms=None, descr=None, image=None):
        item = ListItem(title, synonyms, descr, image)
        self.attach_item(item)

    def _load_data(self):
        return {
            'listSelect': {
                'title': self.title,
                'items': self.list_items
            }
        }
