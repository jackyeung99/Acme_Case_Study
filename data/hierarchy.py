from src.unit_class import Unit

Acme = {
        'Unit': Unit(name='Total', min_contribution=1),
        'Children': [
                {
                'Unit': Unit(name = 'Skin/Body', min_trend=.02, max_trend=.03),
                'Children': []
                },
                {
                'Unit':Unit(name = 'Fragrances'),
                'Children': [
                        {
                        'Unit': Unit(name = 'NA', min_contribution=.21, max_contribution=.30),
                        'Children': []
                        },
                        {
                        'Unit': Unit(name = 'EU', max_trend=.12),
                        'Children': [
                                {
                                'Unit': Unit(name = 'Tools', min_contribution=.03, max_contribution=.07),
                                'Children': [
                                    
                                        {
                                        'Unit': Unit(name = 'Elizabeth_Arden', max_contribution=.13),
                                        'Children': [
                                                {
                                                'Unit': Unit(name = 'Lipstick', revenue=11, margin=.23, min_trend=.06, max_trend=.22, min_contribution=.03, max_contribution=.06),
                                                'Children': []
                                                },
                                                {
                                                'Unit': Unit(name = 'Mascara', revenue=4, margin=.17, min_trend=.03, max_trend=.16, min_contribution=.06, max_contribution=.12),
                                                'Children': []
                                                },
                                                {
                                                'Unit': Unit(name = 'Toner', revenue=3, margin=.08, min_trend=.085, max_trend=.114, min_contribution=.06, max_contribution=.1),
                                                'Children': []
                                                },
                                                {
                                                'Unit': Unit(name = 'Bronzer', revenue=4, margin=.3, min_trend=-.03, max_trend=.14, min_contribution=.01, max_contribution=.03),
                                                'Children': []
                                                },
                                                ]
                                        },
                                        {
                                        'Unit': Unit(name = 'Bobbi Brown', max_contribution=.09),
                                        'Children': [
                                                {
                                                'Unit': Unit(name = 'Lipstick', revenue=3.4, margin=.45, min_trend=-.04, max_trend=.13, min_contribution=.04, max_contribution=.15),
                                                'Children': []
                                                },
                                                {
                                                'Unit': Unit(name = 'Mascara', revenue=3, margin=.10, min_trend=.02, max_trend=.11, min_contribution=.015, max_contribution=.1),
                                                'Children': []
                                                },
                                                ]
                                        },
                                ]
                                },
                                {
                                'Unit': Unit(name = 'Fragrances',min_contribution=0.0, max_contribution=.05),
                                'Children': [
                                    
                                        {
                                                'Unit': Unit(name = 'Killian',min_contribution=.08,  max_contribution=.13),
                                                'Children': [
                                                        {
                                                        'Unit': Unit(name = 'Male Perfume', revenue=1.2, margin=.42, min_trend=.4, max_trend=.8, min_contribution=.03, max_contribution=.15),
                                                        'Children': []
                                                        },
                                                        {
                                                        'Unit': Unit(name = 'Female Perfume', revenue=10, margin=.15, min_trend=.1, max_trend=.2, min_contribution=.05, max_contribution=.11),
                                                        'Children': []
                                                        }
                                                
                                                        ]
                                        },
                                        {
                                                'Unit': Unit(name = 'Frederic Malle',min_contribution=.03, max_contribution=.20, min_trend=-.03, max_trend=.04),
                                                'Children': [
                                                        {
                                                        'Unit': Unit(name = 'Male Perfume', revenue=1, margin=.38, min_trend=.5, max_trend=.9, min_contribution=.01, max_contribution=.10),
                                                        'Children': []
                                                        },
                                                        {
                                                        'Unit': Unit(name='Luxury Exclusive', revenue=7.5, margin=0.60, min_trend=-0.1, max_trend=-.2, min_contribution=0.04, max_contribution=0.08),
                                                        'Children': []
                                                        }
                                        
                                                        ]
                                        },
                                        {
                                                'Unit': Unit(name = 'Balmain', min_contribution=.09, max_contribution=.15),
                                                'Children': [
                                                        {
                                                        'Unit': Unit(name = 'Male Perfume', revenue=2.4, margin=.11, min_trend=-.04, max_trend=.13, min_contribution=.12, max_contribution=.23),
                                                        'Children': []
                                                        },
                                                        {
                                                        'Unit': Unit(name = 'Female Perfume', revenue=4.5, margin=.2, min_trend=0, max_trend=.75, min_contribution=0, max_contribution=.03),
                                                        'Children': []
                                                        }
                                        
                                                        ]
                                                },
                                        ]
                                }




                        ]
                        },
                        {
                        'Unit': Unit(name = 'South_Africa', min_trend=-.15, max_trend=.05),
                        'Children': []
                        },
                        {
                        'Unit': Unit(name = 'Asia', max_contribution=.30),
                        'Children': [
                                 {
                                'Unit': Unit(name = 'Face_Make_Up', min_trend=-.01, max_contribution=.05),
                                'Children': [
                                        {
                                        'Unit': Unit(name = 'Elizabeth_Arden',min_contribution=.08,  max_contribution=.14, max_trend = .07),
                                        'Children': [
                                                {
                                                'Unit': Unit(name = 'Mascara', revenue=1.4, margin=.2, min_trend=-.08, max_trend=-.05, min_contribution=.02, max_contribution=.1),
                                                'Children': []
                                                },
                                                {
                                                'Unit': Unit(name = 'Bronzer', revenue=1.2, margin=.3, min_trend=.05, max_trend=.1, min_contribution=.02, max_contribution=.1),
                                                'Children': []
                                                },
                                                ]
                                        },
                                        {
                                        'Unit': Unit(name = 'Bobbi Brown', min_contribution=.03),
                                        'Children': [
                                                {
                                                'Unit': Unit(name = 'Lipstick', revenue=5, margin=.25, min_trend= -.04, max_trend= -.3, min_contribution=.04, max_contribution=.15),
                                                'Children': []
                                                },
                                                {
                                                'Unit': Unit(name = 'Mascara', revenue=7.8, margin=.15, min_trend= -.09, max_trend=-.11, min_contribution=.015, max_contribution=.1),
                                                'Children': []
                                                },
                                                ]
                                        }
                                        ]
                                },
                        ]
                        },
                ]
                },
                {
                'Unit': Unit(name = 'Hair/ADPO', max_contribution=.30),
                'Children': []
                }
        ]

        }
