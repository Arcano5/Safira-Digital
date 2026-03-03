import React from 'react';
import './App.css';
import logo from './logo.png';

function App() {
  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-container">
          <img src={logo} alt="Safira Digital" className="logo" />
          <ul className="nav-menu">
            <li><a href="#home" className="nav-link">Início</a></li>
            <li><a href="#servicos" className="nav-link">Serviços</a></li>
            <li><a href="#sobre" className="nav-link">Sobre</a></li>
            <li><a href="#contato" className="nav-link">Contato</a></li>
            <li>
              <a 
                href="https://safira-digital-antiats.streamlit.app" 
                className="nav-button"
                target="_blank"
                rel="noreferrer"
              >
                🎯 Anti-ATS
              </a>
            </li>
          </ul>
        </div>
      </nav>

      <section id="home" className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Safira <span className="highlight">Digital</span>
          </h1>
          <p className="hero-subtitle">
            Consultoria que ensina, ensino que transforma.
          </p>
          <p className="hero-description">
            Soluções inteligentes para impulsionar seu negócio
          </p>
          <div className="hero-buttons">
            <a href="#servicos" className="btn-primary">Conheça nossos serviços</a>
            <a 
              href="https://safira-digital-antiats.streamlit.app" 
              className="btn-secondary"
              target="_blank"
              rel="noreferrer"
            >
              🎯 Testar Anti-ATS
            </a>
          </div>
        </div>
      </section>

      <section id="servicos" className="services">
        <h2 className="section-title">Nossos <span className="highlight">Serviços</span></h2>
        <div className="services-grid">
          <div className="service-card">
            <div className="service-icon">🏢</div>
            <h3>Consultoria para PMEs</h3>
            <p>Soluções personalizadas para pequenas e médias empresas crescerem com tecnologia</p>
          </div>
          <div className="service-card">
            <div className="service-icon">🎮</div>
            <h3>Jogos Educativos</h3>
            <p>Aprenda gestão e tecnologia de forma interativa e divertida</p>
          </div>
          <div className="service-card">
            <div className="service-icon">📱</div>
            <h3>Cursos Online</h3>
            <p>Plataforma EAD com cursos práticos e direto ao ponto</p>
          </div>
          <div className="service-card">
            <div className="service-icon">🎯</div>
            <h3>Ferramenta Anti-ATS</h3>
            <p>Otimize seu currículo para passar nos filtros automáticos</p>
            <a 
              href="https://safira-digital-antiats.streamlit.app" 
              className="card-link"
              target="_blank"
              rel="noreferrer"
            >
              Testar grátis →
            </a>
          </div>
          <div className="service-card">
            <div className="service-icon">👥</div>
            <h3>Treinamentos In Company</h3>
            <p>Cursos presenciais sob medida para sua equipe</p>
          </div>
          <div className="service-card">
            <div className="service-icon">📊</div>
            <h3>Gestão Empresarial</h3>
            <p>Ferramentas e metodologias para otimizar resultados</p>
          </div>
        </div>
      </section>

      <section id="sobre" className="about">
        <div className="about-container">
          <div className="about-content">
            <h2 className="section-title">Sobre a <span className="highlight">Safira Digital</span></h2>
            <p className="about-text">
              Estamos dando os primeiros passos com um propósito claro: 
              democratizar o acesso a tecnologia e educação de qualidade 
              para pequenas empresas e profissionais que querem se destacar.
            </p>
            <p className="about-text">
              Hoje somos uma empresa em construção, com muita vontade de 
              aprender e ajudar. Nossas ferramentas estão sendo desenvolvidas 
              com cuidado para oferecer soluções reais e acessíveis.
            </p>
            <p className="about-text highlight-text">
              💡 Transparência é nosso valor: cada cliente, cada curso, 
              cada conquista será comemorada aqui, com vocês.
            </p>
          </div>
          <div className="about-stats">
            <div className="stat">
              <span className="stat-number">Em breve</span>
              <span className="stat-label">Nossos primeiros clientes</span>
            </div>
            <div className="stat">
              <span className="stat-number">Em breve</span>
              <span className="stat-label">Cursos e conteúdos</span>
            </div>
            <div className="stat">
              <span className="stat-number">100%</span>
              <span className="stat-label">Compromisso com a verdade</span>
            </div>
          </div>
        </div>
      </section>

      <section id="contato" className="contact">
        <h2 className="section-title">Conecte-se <span className="highlight">Conosco</span></h2>
        <p className="contact-subtitle">Acompanhe nosso trabalho e tire dúvidas</p>
        
        <div className="social-grid">
          <a 
            href="https://wa.me/5511992095721" 
            className="social-card whatsapp" 
            target="_blank"
            rel="noreferrer"
          >
            <div className="social-icon">📱</div>
            <div className="social-info">
              <h4>WhatsApp</h4>
              <p>Atendimento rápido</p>
            </div>
          </a>
          <a 
            href="https://www.linkedin.com/in/leonildo-freitas-gomes-059a3627b" 
            className="social-card linkedin" 
            target="_blank"
            rel="noreferrer"
          >
            <div className="social-icon">💼</div>
            <div className="social-info">
              <h4>LinkedIn</h4>
              <p>Conteúdo profissional</p>
            </div>
          </a>
          <a 
            href="https://www.youtube.com/channel/UCljQXHVm43eYcRefbpiW9xw" 
            className="social-card youtube" 
            target="_blank"
            rel="noreferrer"
          >
            <div className="social-icon">▶️</div>
            <div className="social-info">
              <h4>YouTube</h4>
              <p>Aulas e dicas</p>
            </div>
          </a>
          <a 
            href="https://www.udemy.com/teaching/?ref=teach_header" 
            className="social-card udemy" 
            target="_blank"
            rel="noreferrer"
          >
            <div className="social-icon">📚</div>
            <div className="social-info">
              <h4>Udemy</h4>
              <p>Cursos completos</p>
            </div>
          </a>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-container">
          <div className="footer-info">
            <img src={logo} alt="Safira Digital" className="footer-logo" />
            <p>Consultoria que ensina, ensino que transforma</p>
          </div>
          <div className="footer-links">
            <div className="footer-column">
              <h4>Serviços</h4>
              <ul>
                <li>Consultoria PMEs</li>
                <li>Jogos Educativos</li>
                <li>Cursos Online</li>
                <li>Anti-ATS</li>
              </ul>
            </div>
            <div className="footer-column">
              <h4>Contato</h4>
              <ul>
                <li>contato@safira.digital</li>
                <li>(11) 99999-9999</li>
              </ul>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 Safira Digital. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;