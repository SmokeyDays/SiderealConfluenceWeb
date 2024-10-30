import FoodSvg from '@/components/icons/items/Food.svg';
import CultureSvg from '@/components/icons/items/Culture.svg';
import IndustrySvg from '@/components/icons/items/Industry.svg';
import InformationSvg from '@/components/icons/items/Information.svg';
import BiotechSvg from '@/components/icons/items/Biotech.svg';
import EnergySvg from '@/components/icons/items/Energy.svg';
import HypertechSvg from '@/components/icons/items/Hypertech.svg';
import WildSmallSvg from '@/components/icons/items/WildSmall.svg';
import WildBigSvg from '@/components/icons/items/WildBig.svg';
import ShipSvg from '@/components/icons/items/Ship.svg';
import ScoreSvg from '@/components/icons/items/Score.svg';
import PlaceholderSvg from '@/components/icons/items/Placeholder.svg';
import JungleSvg from '@/components/icons/items/Jungle.svg';
import IceSvg from '@/components/icons/items/Ice.svg';
import DesertSvg from '@/components/icons/items/Desert.svg';
import WaterSvg from '@/components/icons/items/Water.svg';
import FoodDonationSvg from '@/components/icons/items/FoodDonation.svg';
import CultureDonationSvg from '@/components/icons/items/CultureDonation.svg';
import IndustryDonationSvg from '@/components/icons/items/IndustryDonation.svg';
import InformationDonationSvg from '@/components/icons/items/InformationDonation.svg';
import BiotechDonationSvg from '@/components/icons/items/BiotechDonation.svg';
import EnergyDonationSvg from '@/components/icons/items/EnergyDonation.svg';
import HypertechDonationSvg from '@/components/icons/items/HypertechDonation.svg';
import WildSmallDonationSvg from '@/components/icons/items/WildSmallDonation.svg';
import WildBigDonationSvg from '@/components/icons/items/WildBigDonation.svg';
import ShipDonationSvg from '@/components/icons/items/ShipDonation.svg';
import ScoreDonationSvg from '@/components/icons/items/ScoreDonation.svg';
import ArbitrarySmallSvg from '@/components/icons/items/ArbitrarySmall.svg';
import ArbitraryBigSvg from '@/components/icons/items/ArbitraryBig.svg';
import ArbitraryWorldSvg from '@/components/icons/items/ArbitraryWorld.svg';

export const getIconSvg = (item: string) =>  {
  switch (item) {
    case 'Food':
      return FoodSvg;
    case 'Culture':
      return CultureSvg;
    case 'Industry':
      return IndustrySvg;
    case 'Information':
      return InformationSvg;
    case 'Biotech':
      return BiotechSvg;
    case 'Energy':
      return EnergySvg;
    case 'Hypertech':
      return HypertechSvg;
    case 'WildSmall':
      return WildSmallSvg;
    case 'WildBig':
      return WildBigSvg;
    case 'Ship':
      return ShipSvg;
    case 'Score':
      return ScoreSvg;
    case 'Jungle':
      return JungleSvg;
    case 'Ice':
      return IceSvg;
    case 'Desert':
      return DesertSvg;
    case 'Water':
      return WaterSvg;
    // Donation items
    case 'FoodDonation':
      return FoodDonationSvg;
    case 'CultureDonation':
      return CultureDonationSvg;
    case 'IndustryDonation':
      return IndustryDonationSvg;
    case 'InformationDonation':
      return InformationDonationSvg;
    case 'BiotechDonation':
      return BiotechDonationSvg;
    case 'EnergyDonation':
      return EnergyDonationSvg;
    case 'HypertechDonation':
      return HypertechDonationSvg;
    case 'WildSmallDonation':
      return WildSmallDonationSvg;
    case 'WildBigDonation':
      return WildBigDonationSvg;
    case 'ShipDonation':
      return ShipDonationSvg;
    case 'ScoreDonation':
      return ScoreDonationSvg;
    // Arbitrary inputs
    case 'ArbitrarySmall':
      return ArbitrarySmallSvg;
    case 'ArbitraryBig':
      return ArbitraryBigSvg;
    case 'ArbitraryWorld':
      return ArbitraryWorldSvg;
    default:
      return PlaceholderSvg;
  }
};