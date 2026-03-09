"""Initial schema: languages, phrasal_verbs, user_profiles, exercises + seed data

Revision ID: 0001
Revises: 
Create Date: 2026-03-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, DATETIME2
import uuid

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'languages',
        sa.Column('id', UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('code', sa.String(10), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_target_language', sa.Boolean, nullable=False, server_default=sa.text('0')),
        sa.Column('is_native_language', sa.Boolean, nullable=False, server_default=sa.text('0')),
    )

    op.create_table(
        'phrasal_verbs',
        sa.Column('id', UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('verb', sa.String(100), nullable=False),
        sa.Column('particle', sa.String(50), nullable=False),
        sa.Column('definition', sa.String(500), nullable=False),
        sa.Column('example_sentence', sa.String(1000), nullable=True),
        sa.Column('is_catalog', sa.Boolean, nullable=False, server_default=sa.text('1')),
        sa.Column('created_by_user_id', UNIQUEIDENTIFIER(as_uuid=True), nullable=True),
        sa.Column('created_at', DATETIME2(precision=6), server_default=sa.text('SYSUTCDATETIME()'), nullable=False),
        sa.UniqueConstraint('verb', 'particle', 'created_by_user_id', name='uq_verb_particle_user'),
    )

    op.create_table(
        'user_profiles',
        sa.Column('id', UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('user_id', UNIQUEIDENTIFIER(as_uuid=True), nullable=False, unique=True),
        sa.Column('native_language_id', UNIQUEIDENTIFIER(as_uuid=True),
                  sa.ForeignKey('languages.id'), nullable=False),
        sa.Column('created_at', DATETIME2(precision=6), server_default=sa.text('SYSUTCDATETIME()'), nullable=False),
        sa.Column('updated_at', DATETIME2(precision=6), server_default=sa.text('SYSUTCDATETIME()'), nullable=False),
    )

    op.create_table(
        'user_learning_languages',
        sa.Column('id', UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('user_id', UNIQUEIDENTIFIER(as_uuid=True),
                  sa.ForeignKey('user_profiles.user_id'), nullable=False),
        sa.Column('language_id', UNIQUEIDENTIFIER(as_uuid=True),
                  sa.ForeignKey('languages.id'), nullable=False),
        sa.UniqueConstraint('user_id', 'language_id', name='uq_user_learning_language'),
    )

    op.create_table(
        'user_phrasal_verb_selections',
        sa.Column('id', UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('user_id', UNIQUEIDENTIFIER(as_uuid=True),
                  sa.ForeignKey('user_profiles.user_id'), nullable=False),
        sa.Column('phrasal_verb_id', UNIQUEIDENTIFIER(as_uuid=True),
                  sa.ForeignKey('phrasal_verbs.id'), nullable=False),
        sa.Column('added_at', DATETIME2(precision=6), server_default=sa.text('SYSUTCDATETIME()'), nullable=False),
        sa.UniqueConstraint('user_id', 'phrasal_verb_id', name='uq_user_phrasal_verb'),
    )

    op.create_table(
        'exercise_results',
        sa.Column('id', UNIQUEIDENTIFIER(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('user_id', UNIQUEIDENTIFIER(as_uuid=True), nullable=False, index=True),
        sa.Column('phrasal_verb_id', UNIQUEIDENTIFIER(as_uuid=True),
                  sa.ForeignKey('phrasal_verbs.id'), nullable=False),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('target_language_code', sa.String(10), nullable=False),
        sa.Column('scenario_native', sa.Text, nullable=False),
        sa.Column('sentence_native', sa.Text, nullable=False),
        sa.Column('sentence_target', sa.Text, nullable=False),
        sa.Column('user_answer', sa.Text, nullable=False),
        sa.Column('is_correct', sa.Boolean, nullable=False),
        sa.Column('feedback', sa.Text, nullable=False),
        sa.Column('created_at', DATETIME2(precision=6), server_default=sa.text('SYSUTCDATETIME()'), nullable=False),
    )

    _seed_languages()
    _seed_phrasal_verbs()


def downgrade() -> None:
    op.drop_table('exercise_results')
    op.drop_table('user_phrasal_verb_selections')
    op.drop_table('user_learning_languages')
    op.drop_table('user_profiles')
    op.drop_table('phrasal_verbs')
    op.drop_table('languages')


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def _seed_languages() -> None:
    languages_table = sa.table(
        'languages',
        sa.column('id', UNIQUEIDENTIFIER),
        sa.column('code', sa.String),
        sa.column('name', sa.String),
        sa.column('is_target_language', sa.Boolean),
        sa.column('is_native_language', sa.Boolean),
    )
    rows = [
        # Target languages (can also be native)
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000001'), 'code': 'en', 'name': 'English',            'is_target_language': True,  'is_native_language': True},
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000002'), 'code': 'de', 'name': 'German',             'is_target_language': True,  'is_native_language': True},
        # Native languages (top 5 most spoken + Spanish guaranteed)
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000003'), 'code': 'zh', 'name': 'Mandarin Chinese',   'is_target_language': False, 'is_native_language': True},
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000004'), 'code': 'es', 'name': 'Spanish',            'is_target_language': False, 'is_native_language': True},
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000005'), 'code': 'hi', 'name': 'Hindi',              'is_target_language': False, 'is_native_language': True},
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000006'), 'code': 'ar', 'name': 'Arabic',             'is_target_language': False, 'is_native_language': True},
        {'id': uuid.UUID('a0000001-0000-0000-0000-000000000007'), 'code': 'bn', 'name': 'Bengali',            'is_target_language': False, 'is_native_language': True},
    ]
    op.bulk_insert(languages_table, rows)


def _seed_phrasal_verbs() -> None:
    pv = sa.table(
        'phrasal_verbs',
        sa.column('id', UNIQUEIDENTIFIER),
        sa.column('verb', sa.String),
        sa.column('particle', sa.String),
        sa.column('definition', sa.String),
        sa.column('example_sentence', sa.String),
        sa.column('is_catalog', sa.Boolean),
        sa.column('created_by_user_id', UNIQUEIDENTIFIER),
    )

    def _row(n: int, verb: str, particle: str, defn: str, ex: str) -> dict:
        return {
            'id': uuid.UUID(f'b0000001-0000-0000-0000-{n:012d}'),
            'verb': verb,
            'particle': particle,
            'definition': defn,
            'example_sentence': ex,
            'is_catalog': True,
            'created_by_user_id': None,
        }

    rows = [
        _row(1,   'give',    'up',       'Stop trying or doing something',                          'I gave up smoking last year.'),
        _row(2,   'look',    'forward to','Feel excited about something that is going to happen',   'I look forward to meeting you.'),
        _row(3,   'come',    'up with',  'Think of an idea, plan, or solution',                     'She came up with a brilliant idea.'),
        _row(4,   'turn',    'out',      'Have a particular result or happen in a particular way',  'It turned out to be a great day.'),
        _row(5,   'find',    'out',      'Discover information',                                    'I found out the truth yesterday.'),
        _row(6,   'pick',    'up',       'Lift something or collect someone',                       'Can you pick up the kids from school?'),
        _row(7,   'set',     'up',       'Establish or arrange something',                          'They set up a new company.'),
        _row(8,   'go',      'on',       'Continue or happen',                                      'Please go on with your story.'),
        _row(9,   'carry',   'out',      'Perform or complete a task',                              'We carried out the experiment successfully.'),
        _row(10,  'take',    'off',      'Remove clothing or leave the ground (aircraft)',          'The plane took off on time.'),
        _row(11,  'bring',   'up',       'Mention a topic or raise a child',                       'She brought up an interesting point.'),
        _row(12,  'put',     'off',      'Postpone or delay',                                      'They put off the meeting until Friday.'),
        _row(13,  'work',    'out',      'Exercise or solve a problem',                             'I work out at the gym every morning.'),
        _row(14,  'break',   'down',     'Stop functioning or lose emotional control',              'The car broke down on the highway.'),
        _row(15,  'point',   'out',      'Draw attention to something',                             'He pointed out the mistake in the report.'),
        _row(16,  'come',    'back',     'Return to a place',                                      'When will you come back from vacation?'),
        _row(17,  'get',     'up',       'Rise from bed or stand up',                               'I get up at 6 AM every day.'),
        _row(18,  'look',    'after',    'Take care of someone or something',                      'She looks after her elderly parents.'),
        _row(19,  'run',     'out of',   'Have no more of something',                               'We ran out of milk this morning.'),
        _row(20,  'turn',    'off',      'Stop a device or lose interest',                         'Please turn off the lights.'),
        _row(21,  'turn',    'on',       'Start a device or make it function',                     'Turn on the TV, the show is starting.'),
        _row(22,  'put',     'on',       'Wear clothing or add weight',                            'Put on your coat, it is cold outside.'),
        _row(23,  'take',    'on',       'Accept a responsibility or challenge',                   'She took on extra work this month.'),
        _row(24,  'get',     'along with','Have a good relationship with someone',                 'I get along with my neighbors.'),
        _row(25,  'look',    'up',       'Search for information or improve',                      'Look up the word in a dictionary.'),
        _row(26,  'fill',    'in',       'Complete a form or inform someone',                      'Please fill in the application form.'),
        _row(27,  'give',    'back',     'Return something',                                       'Give back the book when you finish.'),
        _row(28,  'call',    'off',      'Cancel an event or activity',                            'They called off the match due to rain.'),
        _row(29,  'hold',    'on',       'Wait for a short time',                                  'Hold on, I will be right back.'),
        _row(30,  'look',    'into',     'Investigate or examine',                                 'The police are looking into the matter.'),
        _row(31,  'come',    'across',   'Find or meet by chance',                                 'I came across an old photo in the attic.'),
        _row(32,  'get',     'over',     'Recover from something',                                 'It took weeks to get over the flu.'),
        _row(33,  'take',    'up',       'Start a new hobby or activity',                          'He took up painting last year.'),
        _row(34,  'make',    'up',       'Invent a story or reconcile',                            'She made up an excuse for being late.'),
        _row(35,  'cut',     'down on',  'Reduce the amount of something',                         'I need to cut down on sugar.'),
        _row(36,  'put',     'up with',  'Tolerate something unpleasant',                          'I cannot put up with the noise anymore.'),
        _row(37,  'go',      'through',  'Experience something difficult',                         'She went through a tough time last year.'),
        _row(38,  'keep',    'up with',  'Stay at the same level as someone or something',         'It is hard to keep up with technology.'),
        _row(39,  'check',   'in',       'Register at a hotel or airport',                         'We checked in at the hotel at noon.'),
        _row(40,  'check',   'out',      'Leave a hotel or examine something',                     'Check out this new restaurant.'),
        _row(41,  'drop',    'off',      'Deliver someone or something',                           'I will drop off the package on my way.'),
        _row(42,  'show',    'up',       'Arrive or appear',                                       'He finally showed up an hour late.'),
        _row(43,  'end',     'up',       'Finally be in a particular place or situation',          'We ended up staying until midnight.'),
        _row(44,  'hang',    'out',      'Spend time relaxing',                                    'We hang out at the park on weekends.'),
        _row(45,  'figure',  'out',      'Understand or solve something',                          'I cannot figure out this math problem.'),
        _row(46,  'sort',    'out',      'Organize or resolve a problem',                          'We need to sort out this issue quickly.'),
        _row(47,  'let',     'down',     'Disappoint someone',                                     'I am sorry I let you down.'),
        _row(48,  'run',     'into',     'Meet someone unexpectedly',                              'I ran into an old friend at the store.'),
        _row(49,  'stand',   'up for',   'Defend or support something',                            'You should stand up for your rights.'),
        _row(50,  'take',    'over',     'Assume control of something',                            'The new manager took over last week.'),
        _row(51,  'bring',   'about',    'Cause something to happen',                              'The new law brought about many changes.'),
        _row(52,  'get',     'away',     'Escape or go on vacation',                               'They got away for the weekend.'),
        _row(53,  'look',    'out',      'Be careful or watchful',                                 'Look out! There is a car coming.'),
        _row(54,  'pull',    'off',      'Succeed in doing something difficult',                   'She pulled off the impossible.'),
        _row(55,  'pass',    'away',     'Die (polite/euphemistic)',                                'His grandfather passed away last month.'),
        _row(56,  'blow',    'up',       'Explode or suddenly become angry',                       'The balloon blew up with a loud pop.'),
        _row(57,  'shut',    'down',     'Close or stop operating',                                'The factory shut down last year.'),
        _row(58,  'come',    'up',       'Arise or be mentioned',                                  'Something urgent came up at work.'),
        _row(59,  'get',     'along',    'Have a friendly relationship',                           'The kids get along very well.'),
        _row(60,  'go',      'ahead',    'Proceed or start doing something',                       'Go ahead and open your presents.'),
        _row(61,  'back',    'up',       'Support or make a copy',                                 'Please back up your files regularly.'),
        _row(62,  'break',   'up',       'End a relationship or scatter',                          'They broke up after two years.'),
        _row(63,  'catch',   'up',       'Reach the same point as someone else',                   'I need to catch up on my reading.'),
        _row(64,  'cheer',   'up',       'Become or make someone happier',                         'This song always cheers me up.'),
        _row(65,  'clean',   'up',       'Tidy or make clean',                                     'Let us clean up the kitchen.'),
        _row(66,  'close',   'down',     'Stop operating permanently',                             'The shop closed down last month.'),
        _row(67,  'count',   'on',       'Rely on someone',                                        'You can count on me for help.'),
        _row(68,  'cut',     'off',      'Disconnect or isolate',                                  'The storm cut off the power supply.'),
        _row(69,  'deal',    'with',     'Handle or take action on something',                     'I will deal with this problem tomorrow.'),
        _row(70,  'dress',   'up',       'Wear formal or fancy clothes',                           'We dressed up for the gala dinner.'),
        _row(71,  'eat',     'out',      'Have a meal at a restaurant',                            'Let us eat out tonight.'),
        _row(72,  'fall',    'apart',    'Break into pieces or stop working',                      'The old book is falling apart.'),
        _row(73,  'get',     'back',     'Return or retrieve something',                           'When did you get back from your trip?'),
        _row(74,  'give',    'in',       'Surrender or yield',                                     'After hours of debate, he gave in.'),
        _row(75,  'grow',    'up',       'Become an adult',                                        'I grew up in a small town.'),
        _row(76,  'hand',    'in',       'Submit work or a document',                              'Hand in your assignment by Friday.'),
        _row(77,  'head',    'out',      'Leave or start a journey',                               'We should head out before it gets dark.'),
        _row(78,  'keep',    'on',       'Continue doing something',                               'Keep on trying, you will succeed.'),
        _row(79,  'kick',    'off',      'Start something, especially an event',                   'The festival kicked off with a parade.'),
        _row(80,  'lay',     'off',      'Dismiss employees or stop doing something',              'The company laid off 200 workers.'),
        _row(81,  'leave',   'out',      'Omit or exclude',                                        'Do not leave out any important details.'),
        _row(82,  'live',    'up to',    'Meet expectations or standards',                         'The movie lived up to the hype.'),
        _row(83,  'log',     'in',       'Access a computer system with credentials',              'Log in to your account to continue.'),
        _row(84,  'look',    'down on',  'Consider someone inferior',                              'She looks down on people who are rude.'),
        _row(85,  'mess',    'up',       'Make a mistake or cause disorder',                       'I really messed up the presentation.'),
        _row(86,  'move',    'on',       'Progress or leave the past behind',                      'It is time to move on from this issue.'),
        _row(87,  'open',    'up',       'Start talking honestly or unlock',                       'He finally opened up about his feelings.'),
        _row(88,  'opt',     'out',      'Choose not to participate',                              'You can opt out of the newsletter.'),
        _row(89,  'pay',     'back',     'Repay money owed',                                       'I will pay you back next week.'),
        _row(90,  'phase',   'out',      'Gradually stop using something',                         'They plan to phase out the old system.'),
        _row(91,  'pick',    'on',       'Bully or tease someone',                                 'Stop picking on your little brother.'),
        _row(92,  'plug',    'in',       'Connect to an electrical supply',                        'Plug in your phone to charge it.'),
        _row(93,  'put',     'away',     'Store something in its proper place',                    'Put away your toys before dinner.'),
        _row(94,  'rely',    'on',       'Depend on someone or something',                         'We rely on public transport daily.'),
        _row(95,  'rip',     'off',      'Charge too much or steal from someone',                  'That store ripped me off.'),
        _row(96,  'rule',    'out',      'Eliminate as a possibility',                             'The doctor ruled out any serious illness.'),
        _row(97,  'settle',  'down',     'Start living a stable life or become calm',              'They settled down in the countryside.'),
        _row(98,  'sign',    'up',       'Register for something',                                 'Sign up for the course online.'),
        _row(99,  'slow',    'down',     'Reduce speed or become less active',                     'You should slow down on the curves.'),
        _row(100, 'wrap',    'up',       'Finish or complete something',                           'Let us wrap up the meeting now.'),
    ]
    op.bulk_insert(pv, rows)
