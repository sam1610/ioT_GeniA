#!/bin/bash
aws bedrock-runtime converse \
--model-id "amazon.titan-text-premier-v1:0" \
--messages '[{"role":"user","content":[{"text":"Act like you are a smart code generator who writes optimized code along with some test cases based on the defined Input Query.\nPlease follow below instructions while responding:\nInstructions:\n- Output Code in code blocks with appropriate backticks\n- Use Python as your coding language\n- Use various optimization techniques making sure you output the most optimized code\n- Provide atleast 3 test cases and test them with the generated code to show the output\n\nInput Query:\nWrite a function to check whether the two given strings are isomorphic to each other or not.\n"}]}]' \
--inference-config '{"maxTokens":200,"stopSequences":[],"temperature":0,"topP":0.9}' \
--additional-model-request-fields '{}' \
--region us-east-1