# Klare Methode - Project Rules & Guidelines

## 🎯 MVP Mission
Build a **coaching app MVP** that combines **vision boards** and **Wheel of Life** assessments to help users achieve personal growth. Launch in **4 weeks** with **strong core features** that solve real problems.

## 🛠️ Technology Stack
- **Backend**: Django + Django REST Framework
- **Frontend**: HTMX + Alpine.js + TailwindCSS
- **Database**: SQLite (MVP), PostgreSQL (production)
- **Testing**: pytest + pytest-django
- **Deployment**: klare-methode.app

## 📋 Core MVP Features (Week 1-4)
### Must-Have (Launch Critical)
1. **User Authentication** - Registration/Login
2. **Vision Boards** - Create, edit, save visual goal boards
3. **Wheel of Life** - 8-area life assessment with progress tracking
4. **Goal Management** - Set goals linked to life areas
5. **Dashboard** - Overview of boards, assessments, goals

### Should-Have (If Time Permits)
- Basic templates for vision boards
- Progress charts and analytics
- Export functionality

### Won't-Have (Post-MVP)
- Social features
- Team/coach accounts
- Advanced analytics
- Mobile app (React Native later)

## 🧪 Testing Rules
- **Write tests first** for new features (TDD approach)
- **100% model test coverage** minimum
- **API endpoint tests** for all DRF views
- **Frontend integration tests** for critical user flows
- Run tests before every commit: `pytest`

## 🔧 Development Guidelines

### Code Quality
- **DRY Principle**: No code duplication
- **Single Responsibility**: One function/class = one job
- **Readable Code**: Clear variable names, comments for complex logic
- **Type Hints**: Use Python type hints where helpful

### Frontend Rules
- **HTMX First**: Use HTMX for dynamic interactions
- **Alpine.js Second**: Only for complex client-side logic
- **TailwindCSS**: Utility-first CSS approach
- **Mobile-First**: Responsive design from day one

### Backend Rules
- **DRF for APIs**: All data operations through REST APIs
- **Class-Based Views**: Use CBVs for consistency
- **Serializer Validation**: Validate all input data
- **Proper Status Codes**: Use correct HTTP status codes

## 📊 Feature Prioritization Matrix

| Feature | User Value | Complexity | Priority |
|---------|------------|------------|----------|
| Vision Boards | High | Medium | P0 |
| Wheel of Life | High | Low | P0 |
| Goal Tracking | High | Low | P0 |
| User Auth | High | Low | P0 |
| Dashboard | Medium | Medium | P1 |
| Templates | Medium | High | P2 |
| Analytics | Low | High | P3 |

## 🚀 Weekly Milestones

### Week 1: Foundation
- [ ] Project setup with all dependencies
- [ ] User authentication system
- [ ] Basic Django models
- [ ] Test infrastructure
- [ ] Database migrations

### Week 2: Core Features
- [ ] Vision board creation (backend)
- [ ] Wheel of Life assessment (backend)
- [ ] Goal management (backend)
- [ ] API endpoints with tests

### Week 3: Frontend
- [ ] HTMX + Alpine.js integration
- [ ] Vision board interface
- [ ] Wheel of Life visualization
- [ ] Dashboard layout

### Week 4: Polish & Launch
- [ ] Mobile responsiveness
- [ ] User testing
- [ ] Performance optimization
- [ ] Deployment preparation

## ❌ What We Avoid
- **Feature Creep**: Stick to MVP scope
- **Over-Engineering**: Simple solutions over complex ones
- **Technical Debt**: Fix issues immediately, don't accumulate
- **Scope Changes**: No new features without removing others

## 📈 Success Metrics
- **Functional MVP**: All core features working
- **User Experience**: Intuitive and responsive
- **Code Quality**: Well-tested, maintainable code
- **Performance**: Fast loading times
- **Scalability**: Ready for production deployment

## 🔄 Development Workflow
1. **Plan**: Define feature with acceptance criteria
2. **Test First**: Write failing tests
3. **Implement**: Make tests pass
4. **Review**: Code review and testing
5. **Deploy**: Merge and deploy

## 📚 Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Guide](https://alpinejs.dev/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)

---

**Remember**: Quality over quantity. A strong MVP with 5 perfect features beats a mediocre one with 15 half-baked features.