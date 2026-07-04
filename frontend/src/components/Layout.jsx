import Sidebar from './Sidebar';
import Navbar from './Navbar';
import Footer from './Footer';

export default function Layout({ children }) {
  return (
    <div className="app">
      {/* Side route controller */}
      <Sidebar />
      <div className="main-layout">
        {/* Connection health monitor */}
        <Navbar />
        <main className="content">
          {children}
        </main>
        {/* Footnote */}
        <Footer />
      </div>
    </div>
  );
}
