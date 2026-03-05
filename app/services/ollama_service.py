"""
PrepPulse - Ollama Integration Service
"""
import httpx
import json
import re
from typing import List, Optional
from app.core.config import settings


def _build_prompt(student_name, department, cgpa, current_skills, missing_skills, job_title, company_name):
    missing_str = ", ".join(missing_skills) if missing_skills else "none"
    current_str = ", ".join(current_skills[:5]) if current_skills else "none"
    skill1 = missing_skills[0] if missing_skills else "backend development"
    skill2 = missing_skills[1] if len(missing_skills) > 1 else "system design"

    return f"""You are a placement mentor helping {student_name} get a job at {company_name}.

{student_name} is a {department} student with CGPA {cgpa}.
They already know: {current_str}
They need to learn: {missing_str}
The job is: {job_title} at {company_name}

Give them a 3-step study plan. For each step name a real website or YouTube channel they can use (like "freeCodeCamp", "official {skill1} docs", "Traversy Media on YouTube", etc).

Respond with only this JSON and nothing else. Fill every field with real specific content:

{{
  "summary": "{student_name} has {len(missing_skills)} skill(s) to learn before applying to {company_name}. Here is a focused plan.",
  "estimated_weeks": 8,
  "steps": [
    {{
      "step": 1,
      "title": "Learn {skill1}",
      "skill_focus": "{skill1}",
      "duration": "3 weeks",
      "actions": [
        "Go through the official {skill1} documentation from start to finish",
        "Build a small project that uses {skill1} from scratch",
        "Push the project to GitHub with a clear README"
      ],
      "resources": [
        {{"name": "freeCodeCamp {skill1} Tutorial", "url": "https://www.freecodecamp.org", "type": "course"}},
        {{"name": "{skill1} Official Documentation", "url": "https://devdocs.io", "type": "doc"}}
      ],
      "milestone": "A working {skill1} project deployed on GitHub"
    }},
    {{
      "step": 2,
      "title": "Learn {skill2}",
      "skill_focus": "{skill2}",
      "duration": "3 weeks",
      "actions": [
        "Complete a hands-on tutorial for {skill2}",
        "Integrate {skill2} with your Step 1 project",
        "Write documentation explaining what you built"
      ],
      "resources": [
        {{"name": "freeCodeCamp {skill2} Tutorial", "url": "https://www.freecodecamp.org", "type": "course"}},
        {{"name": "{skill2} Official Docs", "url": "https://devdocs.io", "type": "doc"}}
      ],
      "milestone": "A project combining {skill1} and {skill2} on GitHub"
    }},
    {{
      "step": 3,
      "title": "Interview Preparation for {company_name}",
      "skill_focus": "Interview Readiness",
      "duration": "2 weeks",
      "actions": [
        "Solve 25 LeetCode problems on arrays, strings and recursion",
        "Practice explaining your projects out loud in under 3 minutes",
        "Do 2 mock interviews on Pramp"
      ],
      "resources": [
        {{"name": "LeetCode", "url": "https://leetcode.com", "type": "practice"}},
        {{"name": "Pramp Free Mock Interviews", "url": "https://www.pramp.com", "type": "practice"}}
      ],
      "milestone": "25 problems solved and 2 mock interviews completed"
    }}
  ],
  "final_tip": "Study 2 hours every day consistently. {company_name} values problem solving over memorization."
}}"""


def _extract_json(text: str) -> Optional[dict]:
    text = text.strip()
    if text.startswith('['):
        text = text[1:]
    if text.endswith(']'):
        text = text[:-1]
    try:
        return json.loads(text)
    except Exception:
        pass
    for pattern in [r'```json\s*([\s\S]*?)\s*```', r'```\s*([\s\S]*?)\s*```', r'(\{[\s\S]*\})']:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except Exception:
                continue
    return None


async def generate_roadmap(
    student_name: str, department: str, cgpa: float,
    current_skills: List[str], missing_skills: List[str],
    job_title: str, company_name: str,
    required_skills: List[str], preferred_skills: List[str],
    role_type: str, match_percentage: float,
) -> Optional[dict]:

    prompt = _build_prompt(student_name, department, cgpa, current_skills, missing_skills, job_title, company_name)

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1200,
                        "repeat_penalty": 1.1,
                    }
                }
            )
            response.raise_for_status()
            raw_text = response.json().get("response", "")

            print(f"\n=== OLLAMA RAW (first 500 chars) ===")
            print(raw_text[:500])
            print("=== END ===\n")

            roadmap = _extract_json(raw_text)

            if roadmap and "steps" in roadmap and len(roadmap.get("steps", [])) >= 3:
                roadmap["_source"] = "ollama"
                return roadmap
            else:
                print("[PrepPulse] JSON parse failed, using fallback")
                return _fallback_roadmap(missing_skills, job_title, company_name)

    except httpx.ConnectError:
        return _fallback_roadmap(missing_skills, job_title, company_name)
    except Exception as e:
        print(f"[PrepPulse] Ollama error: {e}")
        return _fallback_roadmap(missing_skills, job_title, company_name)


def _fallback_roadmap(missing_skills: List[str], job_title: str, company_name: str) -> dict:
    skill1 = missing_skills[0] if missing_skills else "Core Skills"
    skill2 = missing_skills[1] if len(missing_skills) > 1 else "Projects"

    resource_map = {
        "docker":           [{"name": "Docker Docs", "url": "https://docs.docker.com/get-started/", "type": "doc"}, {"name": "TechWorld with Nana", "url": "https://www.youtube.com/@TechWorldwithNana", "type": "video"}],
        "aws":              [{"name": "AWS Skill Builder", "url": "https://skillbuilder.aws", "type": "course"}, {"name": "AWS Free Tier", "url": "https://aws.amazon.com/free/", "type": "tool"}],
        "react":            [{"name": "React Docs", "url": "https://react.dev/learn", "type": "doc"}, {"name": "Scrimba React", "url": "https://scrimba.com/learn/learnreact", "type": "course"}],
        "node.js":          [{"name": "The Odin Project", "url": "https://www.theodinproject.com", "type": "course"}, {"name": "Node.js Docs", "url": "https://nodejs.org/en/docs", "type": "doc"}],
        "tensorflow":       [{"name": "TensorFlow Tutorials", "url": "https://www.tensorflow.org/tutorials", "type": "doc"}, {"name": "DeepLearning.AI", "url": "https://www.coursera.org/specializations/deep-learning", "type": "course"}],
        "machine learning": [{"name": "Andrew Ng ML Course", "url": "https://www.coursera.org/learn/machine-learning", "type": "course"}, {"name": "fast.ai", "url": "https://www.fast.ai", "type": "course"}],
        "java":             [{"name": "Java Docs", "url": "https://docs.oracle.com/en/java/", "type": "doc"}, {"name": "Amigoscode Java", "url": "https://www.youtube.com/@amigoscode", "type": "video"}],
        "spring boot":      [{"name": "Spring Guides", "url": "https://spring.io/guides", "type": "doc"}, {"name": "Amigoscode", "url": "https://www.youtube.com/@amigoscode", "type": "video"}],
        "mongodb":          [{"name": "MongoDB University", "url": "https://university.mongodb.com", "type": "course"}, {"name": "MongoDB Docs", "url": "https://www.mongodb.com/docs/", "type": "doc"}],
        "sql":              [{"name": "SQLZoo", "url": "https://sqlzoo.net", "type": "practice"}, {"name": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "course"}],
        "python":           [{"name": "Real Python", "url": "https://realpython.com", "type": "course"}, {"name": "Python Docs", "url": "https://docs.python.org/3/tutorial/", "type": "doc"}],
        "javascript":       [{"name": "javascript.info", "url": "https://javascript.info", "type": "doc"}, {"name": "freeCodeCamp JS", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "type": "course"}],
        "rest apis":        [{"name": "REST API Tutorial", "url": "https://restfulapi.net", "type": "doc"}, {"name": "Postman Learning Center", "url": "https://learning.postman.com", "type": "course"}],
        "microservices":    [{"name": "Microservices.io", "url": "https://microservices.io", "type": "doc"}, {"name": "Amigoscode Microservices", "url": "https://www.youtube.com/@amigoscode", "type": "video"}],
    }

    def get_resources(skill):
        key = skill.lower()
        for k, v in resource_map.items():
            if k in key or key in k:
                return v
        return [{"name": "freeCodeCamp", "url": "https://www.freecodecamp.org", "type": "course"},
                {"name": "DevDocs", "url": "https://devdocs.io", "type": "doc"}]

    skills_str = ", ".join(missing_skills[:3]) if missing_skills else "required skills"
    return {
        "summary": f"You have {len(missing_skills)} skill(s) to bridge for {job_title} at {company_name}. Focus on {skills_str} in order.",
        "estimated_weeks": 8,
        "_source": "template",
        "steps": [
            {
                "step": 1, "title": f"Build Proficiency in {skill1}", "skill_focus": skill1,
                "duration": "2-3 weeks",
                "actions": [f"Complete the official {skill1} getting-started guide", f"Build one small project using {skill1}", "Push to GitHub with a README"],
                "resources": get_resources(skill1),
                "milestone": f"A working {skill1} project on GitHub"
            },
            {
                "step": 2, "title": f"Hands-on with {skill2}", "skill_focus": skill2,
                "duration": "2-3 weeks",
                "actions": [f"Complete a structured tutorial on {skill2}", "Combine with Step 1 project", "Write a short README explaining architecture"],
                "resources": get_resources(skill2),
                "milestone": f"Integrated project combining {skill1} and {skill2}"
            },
            {
                "step": 3, "title": "Interview Preparation", "skill_focus": "Interview Readiness",
                "duration": "2 weeks",
                "actions": [f"Solve 25 LeetCode problems relevant to {job_title}", "Walk through your project confidently", "Do 2 mock interviews on Pramp"],
                "resources": [{"name": "LeetCode", "url": "https://leetcode.com", "type": "practice"}, {"name": "Pramp", "url": "https://www.pramp.com", "type": "practice"}],
                "milestone": "25 problems solved and 2 mock interviews completed"
            }
        ],
        "final_tip": "Run `ollama serve` with llama3.2:3b and regenerate for a personalized plan."
    }
