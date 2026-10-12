# functions: 
def build_prompt(topic:str,word_limit:int=150)->str:
    return f"write about {topic},with atmost {word_limit} words"
print(build_prompt("GenAI"))
print(build_prompt("Prompt Engineering",word_limit=300))
#Brushup following concepts:
#*args,**kwargs
#List Comprehension,Dict Comprehension