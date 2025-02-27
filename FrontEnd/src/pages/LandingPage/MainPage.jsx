import MainBanner from './Banner/Banner';
import MainCompanies from './Companies/Companies';
import JoinUs from './JoinUs/JoinUs';
import MainAboutSection from './AboutSection/About';
import css from './MainPage.module.css';
import PropTypes from 'prop-types';
import ChatWidget from '../../components/ChatWidget/ChatWidget';
const MainPage = ({ isAuthorized }) => {
  MainPage.propTypes = {
    isAuthorized: PropTypes.bool,
  };

  return (
    <div className={css['main-app']}>
      <div className={css['chat-widget']}>
        <ChatWidget />
      </div>
      <MainBanner isAuthorized={isAuthorized} />
      <MainCompanies isAuthorized={isAuthorized} />
      {!isAuthorized ? <JoinUs /> : null}
      <MainAboutSection />
    </div>
  );
};

export default MainPage;
