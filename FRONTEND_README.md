# WanderWing Streamlit Frontend

A modern, polished interface for traveler matching and activity recommendations.

---

## Quick Start

### Installation

1. Install dependencies (if not already installed):
```bash
pip install streamlit pandas
```

2. Run the Streamlit app:
```bash
streamlit run src/wanderwing/frontend/app.py
```

3. Open your browser to `http://localhost:8501`

---

## Pages Overview

### 1. 🏠 Home
**Landing page** with overview of the WanderWing workflow.

**Features:**
- Welcome message and product description
- Step-by-step guide
- Quick navigation cards

**What you'll see:**
- Large hero section: "Welcome to WanderWing"
- Three feature cards showing the main workflow steps
- Getting Started section with numbered instructions
- Demo mode notice

---

### 2. 👤 Create Profile
**User profile creation** with verification levels.

**Features:**
- Name, age range, email input fields
- Verification level slider (0-4)
- Dynamic trust score calculation
- Profile summary display

**What you'll see:**
- Clean form with labeled inputs
- Verification slider showing levels:
  - 0 = None
  - 1 = Email Verified
  - 2 = Email + Phone
  - 3 = Email + Phone + ID
  - 4 = Full Verification
- Saved profile summary at bottom
- Success message with confetti animation on save

**User Flow:**
1. Enter name (e.g., "Sarah Chen")
2. Select age range (e.g., "25-34")
3. Enter email
4. Adjust verification slider
5. Click "Save Profile"
6. See success message and profile summary

---

### 3. ✈️ Describe Trip
**Natural language trip description** input.

**Features:**
- Large text area for trip description
- Example descriptions in expandable section
- Real-time parsing simulation
- Validation for minimum length

**What you'll see:**
- Instructional text explaining what to include
- "See Examples" expandable section with 3 sample descriptions:
  - Tokyo hiking/food tour example
  - Paris budget museum tour example
  - Barcelona beach/food combo example
- Large text area (200px height)
- "Parse My Trip" button
- Processing spinner animation
- Success message on completion

**User Flow:**
1. Read examples (optional)
2. Type trip description:
   ```
   I'm planning to visit Tokyo from April 1-10. I love hiking and want
   to do a Mt. Fuji day trip. Also interested in food tours and trying
   authentic ramen. My budget is moderate, around $100/day. I prefer a
   relaxed pace with some free time to explore.
   ```
3. Click "Parse My Trip"
4. See loading spinner (1.5s)
5. Get success message

---

### 4. 🔍 Review Intent
**Side-by-side comparison** of raw text vs. parsed structured data.

**Features:**
- Two-column layout
- Raw text display on left
- Structured parsed data on right
- Confidence score indicator
- Action buttons for approval/editing

**What you'll see:**
- **Left column (Your Description):**
  - Gray box with original text

- **Right column (Parsed Intent):**
  - Blue-bordered box with structured data:
    - Destination: Tokyo
    - Dates: 2024-04-01 to 2024-04-10
    - Duration: 10 days
    - Activities: Hiking, Food Tours, Sightseeing
    - Budget: Moderate
    - Pace: Relaxed
    - Confidence: 85%

- **Action buttons:**
  - "❌ Not Correct - Edit Description"
  - "✅ Looks Good - Find Matches" (primary button)

**User Flow:**
1. Review both columns
2. If correct, click "Looks Good"
3. See loading spinner (2s) while finding matches
4. Get success message with match count

---

### 5. 🤝 Match Results
**Match candidate cards** with compatibility scores.

**Features:**
- Match count header
- Info message about destination/dates
- Match cards showing:
  - Name, age, verification
  - Overall compatibility score (color-coded badge)
  - Explanation text
  - Shared interests tags
  - Safety flags (if any)
  - Expandable compatibility breakdown
- "See Activities" button for each match

**What you'll see:**
- Header: "Found 5 Compatible Travelers"
- Info box about destination
- **Match cards** (example):
  ```
  Alice                                    85% Match [GREEN]
  ⭐⭐⭐ Level 3 • Trust Score: 85%

  Alice is traveling to Tokyo during the same dates and shares
  your interest in Hiking, Food Tours. Great budget compatibility
  and similar travel pace.

  Shared Interests:
  [Hiking] [Food Tours] [Sightseeing]

  ▼ View Compatibility Breakdown

  [See Activities with Alice]
  ```

- **Compatibility breakdown** (expandable):
  - Destination: 100%
  - Date Overlap: 78%
  - Activity Match: 67%
  - Budget: 100%
  - Pace: 80%

**User Flow:**
1. Browse match cards
2. Read explanations
3. Expand compatibility breakdown (optional)
4. Click "See Activities with [Name]"
5. See loading spinner
6. Get success message

---

### 6. 🎯 Activity Recommendations
**Activity cards** with meeting suggestions.

**Features:**
- Context header showing destination and match info
- Activity cards with:
  - Name and score
  - Description
  - Cost and duration
  - Tags
  - Shared interests
  - Meeting suggestion text
- Next steps info box

**What you'll see:**
- **Context box:**
  ```
  📍 Tokyo
  👥 Compatibility Score: 85%
  🎯 Shared Interests: Hiking, Food Tours, Sightseeing
  ```

- **Activity cards** (example):
  ```
  Mount Fuji Day Hike                    Excellent Match

  Day trip to Mt. Fuji with guided trail to 5th station.
  Stunning views, moderate difficulty.

  💰 $50-100   ⏱️ 10 hours

  [outdoors] [adventure]

  Why this matches:
  Both interested in Hiking

  💬 Suggested Message:
  "Looking for a Mount Fuji Day Hike buddy! Interested in
  joining? It takes about 10 hours. We'd need to book in advance."
  ```

**User Flow:**
1. Review recommended activities
2. Read meeting suggestions
3. Copy suggestion text
4. Contact matched traveler (outside app)
5. Click "Leave Feedback" when ready

---

### 7. ⭐ Feedback
**Rating and feedback form** for match quality.

**Features:**
- Match identification
- 1-5 star slider
- Accept/decline/undecided radio buttons
- Comments text area
- Feedback statistics

**What you'll see:**
- Header: "Rating Your Match with Alice"
- **Rating slider:**
  - "How would you rate this match?"
  - Visual: ⭐⭐⭐⭐⭐ (5 stars)

- **Decision radio:**
  - "Yes, we connected!"
  - "No, I declined"
  - "Still deciding"

- **Comments:**
  - Optional text area

- **Submit button**

- **Success response** (after submission):
  - If accepted: Tips for safe meetups
  - If declined: Encouragement to try other matches

- **Statistics:**
  - Average Rating: 4.3 ⭐ (+0.2)
  - Acceptance Rate: 68% (+5%)
  - Total Feedback: 437 (+23)

**User Flow:**
1. Adjust star rating (1-5)
2. Select decision (Yes/No/Deciding)
3. Add comments (optional)
4. Click "Submit Feedback"
5. See thank you message + confetti
6. Read next steps based on decision

---

### 8. 📊 Dashboard
**Experiment metrics and charts** for A/B testing.

**Features:**
- Key metrics grid
- Match acceptance rate line chart (30 days)
- Feedback score by variant bar chart
- Parse success rate area chart (12 weeks)
- Detailed metrics table (expandable)
- Experiment configuration info

**What you'll see:**
- **Metrics Grid:**
  ```
  [Total Matches]  [Acceptance Rate]  [Avg Rating]  [Parse Success]
      487              68%              4.3 ⭐          89%
  ```

- **Line Chart:** "Match Acceptance Rate (Last 30 Days)"
  - X-axis: Dates
  - Y-axis: Acceptance percentage
  - Shows trend over time

- **Bar Chart:** "Average Feedback Score by UX Variant"
  - Variant A (Current): 4.0
  - Variant B (New UI): 4.5 ⭐ [BEST]
  - Variant C (Experimental): 3.9
  - Sample sizes shown below

- **Area Chart:** "Intent Parse Success Rate (Last 12 Weeks)"
  - Shows upward trend from 85% to 91%

- **Insights:**
  - ✅ Variant B performing best
  - 📊 Sample size sufficient
  - 📈 Parse success improved 8%

- **Detailed Metrics** (expandable):
  - Raw data tables
  - Recent acceptance rates
  - Variant performance breakdown

**User Flow:**
1. View key metrics at top
2. Scroll to see charts
3. Read insights
4. Expand detailed metrics (optional)
5. Review experiment configuration

---

## File Structure

```
src/wanderwing/frontend/
├── app.py                          # Main application
├── __init__.py
│
├── pages/                          # Page modules
│   ├── __init__.py
│   ├── create_profile.py          # Profile creation
│   ├── describe_trip.py           # Trip description
│   ├── parsed_intent_review.py    # Intent review
│   ├── match_results.py           # Match cards
│   ├── activity_recommendations.py # Activity cards
│   ├── feedback.py                # Feedback form
│   └── experiment_dashboard.py    # Metrics dashboard
│
├── components/                     # Reusable components
│   ├── __init__.py
│   ├── cards.py                   # Match & activity cards
│   └── charts.py                  # Dashboard charts
│
└── utils/                          # Utilities
    ├── __init__.py
    ├── styling.py                 # CSS and styling
    ├── session.py                 # Session state
    └── mock_data.py               # Demo data generators
```

---

## Key Features

### Modern UI
- Clean, professional design
- Consistent color scheme (blue gradients)
- Smooth animations and transitions
- Responsive layout

### Navigation
- Sidebar navigation with icons
- Clear page progression
- Step-by-step workflow

### Data Visualization
- Line charts for trends
- Bar charts for comparisons
- Area charts for success rates
- Metric cards with deltas

### User Experience
- Form validation
- Loading spinners
- Success messages with confetti
- Info boxes and warnings
- Expandable sections
- Tooltips and help text

---

## Demo Data

The frontend uses **mock data generators** from `utils/mock_data.py`:

- **`generate_parsed_intent()`**: Extracts destination, dates, activities from text
- **`generate_mock_matches()`**: Creates 5 compatible traveler profiles
- **`generate_mock_activities()`**: Generates activity recommendations
- **`generate_dashboard_metrics()`**: Creates dashboard metrics
- **`generate_acceptance_rate_by_day()`**: Generates trend data
- **`generate_feedback_by_variant()`**: Creates A/B test results

All data is **realistic and varied** to demonstrate the full system.

---

## Session State

User data persists across pages using Streamlit session state:

- **Profile**: Name, age, verification, trust score
- **Trip Text**: Raw description
- **Parsed Intent**: Structured data
- **Matches**: List of compatible travelers
- **Activities**: Recommended activities
- **Feedback**: User ratings and comments
- **Experiment Variant**: A/B test assignment

Managed in `utils/session.py` with helper functions:
- `save_profile()`, `get_profile()`
- `save_trip_description()`, `get_trip_text()`
- `save_matches()`, `get_matches()`
- etc.

---

## Styling

Custom CSS in `utils/styling.py`:

- **Cards**: Rounded corners, shadows, borders
- **Tags**: Colored pills for categories
- **Badges**: Color-coded score indicators
- **Metrics**: Large numbers with labels
- **Forms**: Rounded inputs with borders
- **Buttons**: Hover effects and transitions

**Color Palette:**
- Primary Blue: `#1E3A8A`, `#2563EB`, `#3B82F6`
- Success Green: `#10B981`, `#DEF7EC`
- Warning Yellow: `#F59E0B`, `#FEF3C7`
- Neutral Gray: `#6B7280`, `#F9FAFB`

---

## Production Integration

To connect to real backend:

1. **Replace mock data** calls with API calls:
   ```python
   # Current (mock):
   matches = generate_mock_matches(profile, intent)

   # Production:
   response = requests.post("http://api/matches", json={"profile": profile, "intent": intent})
   matches = response.json()["matches"]
   ```

2. **Update intent parsing**:
   ```python
   # Current (mock):
   parsed = generate_parsed_intent(text)

   # Production:
   response = requests.post("http://api/parse-intent", json={"text": text})
   parsed = response.json()["intent"]
   ```

3. **Connect activity recommender**:
   ```python
   # Current (mock):
   activities = generate_mock_activities(match, intent)

   # Production:
   response = requests.post("http://api/activities", json={"match": match, "intent": intent})
   activities = response.json()["recommendations"]
   ```

4. **Store feedback**:
   ```python
   # Current (session only):
   save_feedback(match_id, rating, comments, accepted)

   # Production:
   requests.post("http://api/feedback", json={"match_id": match_id, "rating": rating, ...})
   ```

---

## Screenshots Description

### Home Page
- Large "Welcome to WanderWing" header
- 3-column grid with feature cards (profile, trip, matches)
- 2-column grid with activities and feedback cards
- Getting started section with numbered steps
- Blue demo mode notice at bottom

### Create Profile
- Clean form with 4 inputs (name, age, email, verification)
- Slider showing verification levels 0-4
- Save button (blue, full width)
- Profile summary box after saving

### Describe Trip
- Instructional text at top
- Expandable "See Examples" section
- Large text area (white background, rounded corners)
- "Parse My Trip" button (blue, full width)
- Gray box showing saved description after parsing

### Review Intent
- Two-column comparison:
  - Left: Gray box with raw text
  - Right: Blue box with structured data (table format)
- Confidence score in green at bottom right
- Two buttons: red "Not Correct" and green "Looks Good"

### Match Results
- "Found 5 Compatible Travelers" header
- Blue info box with destination
- 5 match cards with:
  - Blue gradient background
  - Name in large bold text
  - Score badge (green for high, yellow for medium)
  - Explanation paragraph
  - Shared interest tags (blue pills)
  - Expandable breakdown (white box inside card)
  - "See Activities" button below each card

### Activity Recommendations
- Blue context box at top (destination, score, interests)
- 5 activity cards (white background, gray border):
  - Activity name in large text
  - Score badge in top right
  - Description text
  - Icons for cost and duration
  - Colored tags
  - Gray "Why this matches" section
  - Blue "Suggested Message" box at bottom (with quote text)

### Feedback
- "Rating Your Match with Alice" header
- Star slider showing 1-5 stars
- Radio buttons for accept/decline
- Text area for comments
- Submit button (blue, full width)
- 3-column metrics at bottom (rating, acceptance, total)

### Dashboard
- 4-column metrics grid (large numbers with labels)
- Line chart (blue line, 30 days)
- Bar chart (3 colored bars for variants)
- Sample size table below bar chart
- Area chart (green gradient, 12 weeks)
- Success/info boxes with insights
- Expandable "View Raw Data" section

---

## Tips

- **Navigation:** Use sidebar on left to jump between pages
- **Demo flow:** Go through pages 1-7 in order for full experience
- **Dashboard:** Page 8 can be viewed anytime
- **Refresh:** Click browser refresh to reset all session data
- **Mock data:** Changes slightly on each run (randomized)

---

## Troubleshooting

**"Module not found" errors:**
```bash
# Make sure you're in the right directory
cd /path/to/wanderwing

# Run from project root
streamlit run src/wanderwing/frontend/app.py
```

**Import errors:**
```bash
# Install dependencies
pip install streamlit pandas

# If using virtual environment, activate it first
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

**Page not loading:**
- Check that you're running from project root
- Verify all `__init__.py` files exist
- Check browser console for JavaScript errors

---

## Next Steps

1. **Test the demo:** Run through all pages to see the workflow
2. **Review mock data:** Check `utils/mock_data.py` for data generation logic
3. **Customize styling:** Modify `utils/styling.py` for different colors/fonts
4. **Add real data:** Connect to actual backend APIs
5. **Deploy:** Use Streamlit Cloud, Heroku, or Docker for deployment

---

**Built with Streamlit** - Modern, Pythonic, and Beautiful! 🎨
