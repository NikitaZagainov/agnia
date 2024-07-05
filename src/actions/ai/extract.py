from src.utils.base import prepare_prompt
from src.actions.registry import register_action
from src.external_services.llm import LLM
from src.actions.ai.base import Action
from src.models.extract_params import ExtractInputParams, ExtractOutputParams


class Extract(Action[ExtractInputParams, ExtractOutputParams]):

    def __init__(
        self,
        action_name,
        stop=None,
        max_tokens=None,
    ):
        super().__init__(action_name)
        self.llm = LLM()  
        
        self.stop = stop
        self.max_tokens = max_tokens
        self.temperature = 0.1

    def get_prompt(self) -> str:
        return "PROMPT"
    
    async def execute(self, input_data: ExtractInputParams) -> ExtractOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {
                "prompt": prompt,
                "stop": self.stop,
                "max_tokens": self.max_tokens
            }
        )
        return ExtractOutputParams(answer=answer)


@register_action(ExtractInputParams, ExtractOutputParams, system_name = 'GitFlame')
class ExtractIssueTitle(Extract):
    action_name = "extract_issue_title"

    def __init__(self):
        super().__init__(self.action_name, stop="</Answer>", max_tokens=50)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
You are a text analysis expert. You are given a user review. Your goal is to create a title for this review. Structure your answer as a single sentence, write in English, and use natural language only.
</Instruction>

<Example>
<User review>My 7 day free trial ended recently and money 56usd was automatically deducted from the card. There is no way to refund because it's not according to "some policies". Then I tried to use your app but still my account shows free account. I tried multiple times to resolve this issue through their support email but the same email keeps coming to me. It's been more than a week now. My account is not yet upgraded. Now I'm deeply frustrated. I lost my valuable money and also paid subscription.</User review>
<Answer>Subscription is not working</Answer>
</Example>

<Example>
<User review>I installed it 1-25-24 for the first time, and immediately it says "Please update, this version is no longer supported." Clicking the update button does nothing. So I can't get into the app at all.</User review>
<Answer>New app version asks for an update.</Answer>
</Example>

<Example>
<User review>{USER_REQUEST}</User review>
<Answer>"""


@register_action(ExtractInputParams, ExtractOutputParams, system_name = 'GitFlame')
class ExtractIssueBody(Extract):
    action_name = "extract_issue_body"

    def __init__(self):
        super().__init__(self.action_name, stop="</Answer>", max_tokens=1000)
        
    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
You are a text analysis expert. You are given an unstructured user request. Your goal is understand the problem the user is facing and to highlight the information relevant to the problem. The request may also contain unrelated information. You should only write the highlighted parts of the text. Structure your answer in a technical format in the original language, only use natural language.
</Instruction>


<Example>
<User review>My 7 day free trial ended recently and money 56usd was automatically deducted from the card. There is no way to refund because it's not according to "some policies". Then I tried to use your app but still my account shows free account. I tried multiple times to resolve this issue through their support email but the same email keeps coming to me. It's been more than a week now. My account is not yet upgraded. Now I'm deeply frustrated. I lost my valuable money and also paid subscription.</User review>
<Answer>After the 7 day free trial ended and the payment with a card was made, the account still shows as a free account.</Answer>
</Example>

<Example>
<User review>I installed the latest app version 1.2.3 on 1-25-24 for the first time, and immediately it says "Please update, this version is no longer supported." Clicking the update button does nothing. So I can't get into the app at all. I use arch btw</User review>
<Answer>On arch OS, the latest app version 1.2.3 installed on 1-25-24 says "Please update, this version is no longer supported.". Clicking the update button does nothing.</Answer>
</Example>

<Example>
<User review>{USER_REQUEST}</User review>
<Answer>"""
