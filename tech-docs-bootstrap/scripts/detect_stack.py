#!/usr/bin/env python3
import os
import json
import sys

def detect_stack(project_root):
    stack = {
        "frameworks": [],
        "languages": [],
        "data_layer": [],
        "infrastructure": [],
        "testing": []
    }

    # Files to look for and what they indicate
    indicators = {
        "package.json": ("languages", "Node.js"),
        "requirements.txt": ("languages", "Python"),
        "pyproject.toml": ("languages", "Python"),
        "go.mod": ("languages", "Go"),
        "Cargo.toml": ("languages", "Rust"),
        "Gemfile": ("languages", "Ruby"),
        "composer.json": ("languages", "PHP"),
        "next.config.js": ("frameworks", "Next.js"),
        "next.config.mjs": ("frameworks", "Next.js"),
        "nuxt.config.js": ("frameworks", "Nuxt.js"),
        "nuxt.config.ts": ("frameworks", "Nuxt.js"),
        "svelte.config.js": ("frameworks", "SvelteKit"),
        "angular.json": ("frameworks", "Angular"),
        "astro.config.mjs": ("frameworks", "Astro"),
        "prisma/schema.prisma": ("data_layer", "Prisma"),
        "drizzle.config.ts": ("data_layer", "Drizzle ORM"),
        "Dockerfile": ("infrastructure", "Docker"),
        "docker-compose.yml": ("infrastructure", "Docker Compose"),
        "serverless.yml": ("infrastructure", "Serverless Framework"),
        "terraform": ("infrastructure", "Terraform"),
        "vercel.json": ("infrastructure", "Vercel"),
        "netlify.toml": ("infrastructure", "Netlify"),
        "jest.config.js": ("testing", "Jest"),
        "jest.config.ts": ("testing", "Jest"),
        "vitest.config.ts": ("testing", "Vitest"),
        "pytest.ini": ("testing", "Pytest"),
        "cypress.json": ("testing", "Cypress"),
        "playwright.config.ts": ("testing", "Playwright"),
    }

    for root, dirs, files in os.walk(project_root):
        # Prevent searching too deep
        if root.count(os.sep) - project_root.count(os.sep) > 2:
            continue
            
        for file in files:
            if file in indicators:
                category, tech = indicators[file]
                if tech not in stack[category]:
                    stack[category].append(tech)

        # Check directories
        for d in dirs:
            if d == "terraform":
                if "Terraform" not in stack["infrastructure"]:
                    stack["infrastructure"].append("Terraform")
            elif d == "supabase":
                if "Supabase" not in stack["data_layer"]:
                    stack["data_layer"].append("Supabase")
            elif d == "cypress":
                if "Cypress" not in stack["testing"]:
                    stack["testing"].append("Cypress")

    # Simple package.json parsing for obvious frontends if node exists
    pkg_path = os.path.join(project_root, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, "r") as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "react" in deps and "React" not in stack["frameworks"]:
                    stack["frameworks"].append("React")
                if "vue" in deps and "Vue" not in stack["frameworks"]:
                    stack["frameworks"].append("Vue")
                if "tailwindcss" in deps and "Tailwind CSS" not in stack["frameworks"]:
                    stack["frameworks"].append("Tailwind CSS")
                if "typescript" in deps and "TypeScript" not in stack["languages"]:
                    stack["languages"].append("TypeScript")
        except:
            pass

    return stack

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(detect_stack(target_dir), indent=2))
