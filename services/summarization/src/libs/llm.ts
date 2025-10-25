import Groq from "groq-sdk";

export const LLM = async (client: Groq, systemPrompt: string, context: string, model: string = "openai/gpt-oss-20b") => {
  const chatCompletion = await client.chat.completions.create({
    messages: [
      {
        role: "system",
        content: systemPrompt,
      },
      {
        role: "user",
        content: `${context}`,
      }
    ],
    model
  })


  return JSON.parse(chatCompletion.choices[0].message.content)
}
