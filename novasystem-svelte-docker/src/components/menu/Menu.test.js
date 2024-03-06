// Menu.test.js
import { render } from '@testing-library/svelte';
import Menu from './Menu.svelte';

describe('Menu component', () => {
  test('should render correctly with no items', () => {
    const { container } = render(Menu, { menuItems: [] });
    expect(container.querySelector('nav')).not.toBeNull();
    expect(container.querySelectorAll('li').length).toBe(0);
  });

  test('should display items when provided', () => {
    const items = [{ id: 'home', name: 'Home', link: '/home' }, { id: 'about', name: 'About', link: '/about' }];
    const { getByText } = render(Menu, { menuItems: items });

    expect(getByText('Home')).toBeInTheDocument();
    expect(getByText('About')).toBeInTheDocument();
  });
});
