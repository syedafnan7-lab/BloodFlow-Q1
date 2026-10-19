import { Activity, ArrowRight, Play } from 'lucide-react';
import Orb from '../components/Orb';
import DotGrid from '../components/DotGrid';
import MagicRings from '../components/MagicRings';
import TiltedCard from '../components/TiltedCard';
import TextType from '../components/TextType';
import SpecularButton from '../components/SpecularButton';

export default function Home({ onNavigate, researcherName = '', theme = 'light' }) {
  const welcomeName = researcherName.trim() || 'Researcher';
  return <div className="home-page">
    <section className="home-hero">
      <div className="home-hero-effects" aria-hidden="true">
        <DotGrid className="home-dot-field" dotSize={1.4} gap={24} baseColor="#8d99ae" activeColor="#ef233c" opacity={0.48} glow={0.5} swell={0.4} intro={false} mouseInteraction={false} clickShock={false} />
        <Orb className="home-orb" colors={['#ef233c', '#8d99ae', '#2b2d42']} backgroundColor="#000000" size={0.8} glow={0.7} opacity={0.5} speed={0.35} followCursor={false} clickPulse={false} intro={false} />
      </div>
      <div className="home-hero-content">
        <a className="home-brand-lockup" href="/" aria-label="BloodFlow-Q home"><img src="/bloodflow-q-logo.webp" alt="" /><span>BloodFlow<span>-Q</span><small>QUANTUM LOGISTICS RESEARCH</small></span></a>
        <p className="home-kicker">SYNTHETIC RESEARCH WORKSPACE <span><i /> SYSTEM READY</span></p>
        <TextType as="h1" text={`Welcome back, ${welcomeName}.`} typingSpeed={24} loop={false} showCursor={false} typeEffect="fade" />
        <p className="home-lede">Model blood logistics as a network decision problem. Explore hospital demand, test route disruptions, and compare classical and quantum-assisted allocation methods.</p>
        <div className="home-actions">
          <SpecularButton className="home-primary-action" size="md" radius={12} tint="#ef233c" textColor="#fff" lineColor="#ff9aa8" baseColor="#d90429" onClick={() => onNavigate('dashboard')}><Activity size={16} /> Open research dashboard <ArrowRight size={16} /></SpecularButton>
          <button type="button" className="home-secondary-action" onClick={() => onNavigate('optimization')}><Play size={15} /> Start an optimization</button>
        </div>
      </div>
      <div className="home-hero-visual" aria-hidden="true"><MagicRings className="home-magic-rings" color="#ef233c" colorTwo="#8d99ae" ringCount={7} motion="pulse" speed={0.45} lineThickness={1.5} glow={1.1} baseRadius={0.29} radiusStep={0.105} rotation={-18} tilt={23} opacity={0.85} followMouse={false} clickBurst={false} intro theme={theme} /><div className="home-visual-orbit orbit-one" /><div className="home-visual-orbit orbit-two" /><TiltedCard className="home-visual-tilt" imageSrc="/bloodflow-q-logo.webp" altText="BloodFlow-Q quantum logistics mark" containerWidth="190px" containerHeight="190px" imageWidth="160px" imageHeight="160px" rotateAmplitude={9} glare={0.28} shadow={0.26} parallax={0.3} showTooltip={false} intro={false} /><div className="home-visual-label"><i /> NETWORK MODEL <b>v2.001</b></div></div>
    </section>
  </div>;
}
