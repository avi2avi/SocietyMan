# Enhancement Plan - BillBox Features into SocietyMan

Based on analysis of BillBox (Laravel-based society management) and SocietyMan (FastAPI/React-based), the following enhancements will be implemented:

## 1. 🌓 Dark/Light Theme Toggle (Primary Enhancement)
- Implement full dark mode using CSS custom properties
- Toggle button in the topbar with sun/moon icons
- Persist preference in localStorage

## 2. ⚡ Maintenance Mode
- Backend: Add maintenance_mode field to settings table
- API endpoint to toggle maintenance mode
- Frontend: Maintenance page displayed for non-admin users when mode is active

## 3. 🎨 UI Polish & Refinements
- BillBox Soft UI Dashboard-inspired design touches
- Enhanced card styles with softer shadows and gradients
- Improved typography and spacing