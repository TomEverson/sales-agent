# Agent Workflow & Conversation Guide

This document describes how the AI agent handles conversations and executes the booking workflow.

---

## Conversation Flow

### 1. Initial User Contact

When a user first contacts the bot:
1. Bot sends welcome message
2. Bot prompts language selection (English 🇬🇧 / Burmese 🇲🇲)
3. User selects language via inline keyboard

### 2. Processing User Messages

For each incoming message:
1. **Language Detection**: Check if user has set a language preference
2. **History Retrieval**: Load conversation history (max 20 messages)
3. **Agent Processing**: Pass message + history to Claude agent
4. **Response Delivery**: Send Claude's response back to user
5. **History Update**: Append conversation to memory

---

## Agent Decision Making

### Information Extraction

Before calling any tools, the agent extracts:

1. **Destination** - Where does user want to go?
2. **Travel Dates** - When do they want to travel? (or "flexible")
3. **Budget** - How much do they want to spend? (required!)
4. **Number of Travelers** - How many people? (default: 1)
5. **Passport Country** - For visa checks

If any required information is missing, the agent asks clarifying questions (max 2 per turn).

### Search Strategy

The agent follows this exact search order:

1. `search_flights` - origin → destination
2. `search_hotels` - destination city
3. `search_activities` - destination city
4. `search_transport` - airport → city center (optional)

Rules:
- Always run all relevant searches before responding
- Adapt if search returns no results (try without filters)
- Never tell user a search "failed" - just adapt silently

---

## Package Building

### Selection Rules

**Flights:**
- Prefer economy class unless user specifies otherwise
- Pick best price that fits budget
- Never select flight with 0 seats available

**Hotels:**
- Estimate nights from dates (default: 2 if flexible)
- Pick highest star rating within remaining budget
- Never select hotel with 0 rooms available

**Activities:**
- Always include at least 1 activity
- Include up to 3 activities if budget allows
- Prioritize variety of categories

**Transport:**
- Include only if adds clear value (airport pickup)
- Omit if budget is tight

### Budget Validation

- Total must NOT exceed user's budget
- If no valid package exists within budget, tell user honestly
- Present minimum possible package and ask if they want to proceed

---

## Booking Workflow

### Step 1: Package Presentation

After building a package:
- Present complete tour package in formatted form
- Show total cost and budget remaining
- End with tweak invitation: "Would you like me to adjust anything?"

### Step 2: User Confirms Package

If user says "yes" or "book it":

**Collect traveler information:**
1. Full name (for all bookings)
2. Contact email (for confirmations)
3. Number of travelers (default: 1)

**Collect booking details:**
- Flight: number of seats
- Hotel: check-in/check-out dates
- Activity: date for each activity
- Transport: confirm details

### Step 3: Booking Summary

Present complete summary including:
- All items with prices
- Insurance options (Basic $15, Standard $35, Premium $65)
- Total for all travelers
- Ask: "Would you like to add insurance?"

### Step 4: Payment Initiation

**CRITICAL: Payment MUST be initiated BEFORE bookings are created**

1. Call `initiate_payment` with total amount
2. Show payment reference (PAY-XXXXXX)
3. Request payment screenshot
4. **DO NOT create bookings yet**

### Step 5: Payment Confirmation

When user sends screenshot:
1. Call `confirm_payment` with booking reference
2. Only if payment confirmed → create bookings

### Step 6: Create Bookings

After payment confirmed, book in this order:
1. `book_flight`
2. `book_hotel`
3. `book_activity` (for each)
4. `book_transport` (if applicable)
5. `add_insurance` (if selected)

**CRITICAL: If ANY booking fails, STOP IMMEDIATELY. Do not proceed.**

### Step 7: Post-Booking

After successful booking:
1. Show all booking confirmations with reference numbers
2. Call `get_weather` for destination
3. Display weather forecast with travel tips

---

## Tweak Requests

When user requests changes:

### "Nicer hotel" / "Upgrade hotel"
- Re-search with higher stars filter
- Recalculate and present full updated package

### "Cheaper hotel" / "Budget hotel"
- Re-search with lower max_price filter
- Recalculate and present full updated package

### "Different flight" / "Earlier/Later flight"
- Re-search flights
- Present alternatives and ask user to pick

### "More activities" / "Add activity"
- Re-search activities
- Suggest options within budget

### "Remove activity"
- Remove from package
- Recalculate and present updated package

### "Add transport"
- Search transport airport → city center
- Add to package if found

**Always present the complete updated package after any tweak, not just the changed component.**

---

## Error Handling

### When to Escalate to Human

- API or service unavailable (connection errors, timeouts)
- Booking creation fails after payment confirmed
- User explicitly asks to speak with human
- Same issue fails repeatedly (2-3 attempts)
- Payment processing errors

### Escalation Process

1. Acknowledge the issue clearly and sincerely
2. Apologize for the inconvenience
3. Explain briefly what went wrong (no technical jargon)
4. Offer to connect with human operator
5. Call `get_operator_contact` tool

### Example Escalation Message

> "I'm sorry, I've encountered an issue that I can't resolve on my own: the booking system is temporarily unavailable. I apologize for any inconvenience. Let me connect you with one of our human operators who can help directly."

---

## Tool Reference

### Search Tools

| Tool | Purpose |
|------|---------|
| `search_flights` | Find available flights |
| `search_hotels` | Find available hotels |
| `search_activities` | Find activities/experiences |
| `search_transport` | Find transport options |

### Booking Tools

| Tool | Purpose |
|------|---------|
| `book_flight` | Create flight booking |
| `book_hotel` | Create hotel booking |
| `book_activity` | Create activity booking |
| `book_transport` | Create transport booking |
| `add_insurance` | Add travel insurance |

### Information Tools

| Tool | Purpose |
|------|---------|
| `check_visa` | Check visa requirements |
| `get_weather` | Get weather forecast |
| `get_insurance_plans` | View insurance options |
| `get_operator_contact` | Get human help |

### Payment Tools

| Tool | Purpose |
|------|---------|
| `initiate_payment` | Start payment process |
| `confirm_payment` | Confirm payment received |
| `check_payment_status` | Check payment status |

---

## Language Support

### Supported Languages

- **English** (en) - Default
- **Burmese** (my) - Myanmar language

### Switching Languages

User can switch language at any time using the inline keyboard. The agent loads the appropriate system prompt (`system_prompt.md` for English, `system_prompt_my.md` for Burmese).

---

## Conversation Memory

- Maximum 20 messages stored per user
- History is persisted to JSON files
- Data stored in: `salebot/data/conversations.json` and `salebot/data/preferences.json`
- User can clear history with `/clear` command

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start conversation, show welcome message |
| `/clear` | Clear conversation history and start fresh |

---

## Special Handling

### Photo/Screenshot Handling

- If user sends a photo, it's treated as a payment screenshot
- Bot extracts booking reference from message and confirms payment

### Out-of-Stock Items

- Search results automatically filter out items with 0 availability
- If booked item becomes unavailable during booking process, inform user and search alternatives

### Budget Too Low

- If no valid package exists within budget, tell user honestly
- Present minimum possible package and ask if they want to proceed