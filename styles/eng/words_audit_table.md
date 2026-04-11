# Image Audit Table

This table tracks the quality of generated images for every word defined in `words.py`.

**Columns:**
- **Word**: The word from the list.
- **Concept**: The specific generation prompt from `words.py`.
- **Understood by 5-6 yo?**: Is the image immediately recognizable and appropriate for a child?
- **Visual Guideline (Bg/Style)?**: Does it follow the style rules (flat vector, white bg, thick outline, etc.)?
- **Regenerate?**: Flag if the image needs to be re-generated.
- **Matches Concept?**: Does the image match the specific details requested in the concept prompt?
- **Note**: Additional observations or specific issues (e.g., "wrong color", "missing detail").

| Word | Concept | Understood (5-6 yo)? | Visual Guideline (Bg/Style)? | Regenerate? | Matches Concept? | Note |
|---|---|---|---|---|---|---|
| people | two simple standing figures, different heights | | | | | |
| man | man, adult male with short hair and beard | | | | | |
| person | gender-neutral figure, question mark above head | | | | | |
| men | two adult males side by side, distinct poses | | | | | |
| face | simple smiling face, two dots and curved mouth | | | | | |
| body | human torso only, arms at sides, no head | | | | | |
| hand | open palm facing forward, five fingers clearly visible | | | | | |
| head | round human head, side profile, simple neck line | | | | | |
| family | three stick figures holding hands, adult-adult-child | | | | | |
| friends | two smiling faces close together, matching height | | | | | |
| friend | single waving figure, one hand raised high | | | | | |
| guys | two casual male figures, caps on heads | | | | | |
| girl | girl, young female child with ponytail and dress | | | | | |
| boy | boy, young male child with short hair and shorts | | | | | |
| child | small figure, oversized head, playful stance | | | | | |
| kid | small figure jumping, arms up, simple clothes | | | | | |
| baby | baby, infant in swaddle, round head, sitting | | | | | |
| father | man, adult male standing with hand on hip | | | | | |
| mother | woman, adult female with gentle open arms | | | | | |
| mom | woman, adult female wearing simple apron outline | | | | | |
| dad | man, adult male with tool pocket outline | | | | | |
| son | boy, young male holding colorful balloon | | | | | |
| daughter | girl, young female holding single flower | | | | | |
| woman | woman, adult female with long hair and dress | | | | | |
| wife | woman with visible ring on finger, gentle pose | | | | | |
| husband | man with visible tie outline, confident stance | | | | | |
| lady | woman wearing elegant hat, polite posture | | | | | |
| student | child with backpack outline, holding book | | | | | |
| guy | young male, backward cap, hands in pockets | | | | | |
| king | king, ornate crown with jewel dots | | | | | |
| queen | queen, crown with veil outline, elegant | | | | | |
| prince | prince, small crown on youthful head | | | | | |
| captain | captain hat with anchor badge, simple | | | | | |
| doctor | doctor, white coat with stethoscope outline | | | | | |
| coach | coach, whistle around neck, clipboard in hand | | | | | |
| artist | artist, beret on head, paintbrush in hand | | | | | |
| player | athlete in uniform, ball at feet | | | | | |
| winner | trophy cup with star burst behind it | | | | | |
| home | home, cozy cottage shape with heart on door | | | | | |
| house | house, simple rectangle with triangular roof and door | | | | | |
| building | building, tall rectangular block with grid windows | | | | | |
| room | room, square cutaway showing bed and window | | | | | |
| school | school, brick building with bell tower and flag | | | | | |
| town | town, cluster of small houses with church steeple | | | | | |
| village | village, two cottages with wooden fence | | | | | |
| hotel | hotel, multi-story block with large H sign | | | | | |
| store | store, shopfront with striped awning | | | | | |
| shop | shop, small doorway with goods silhouette visible | | | | | |
| station | station, platform roof over simple bench | | | | | |
| airport | airport, terminal building with plane silhouette | | | | | |
| park | park, bench under leafy tree, winding path | | | | | |
| field | field, wide green grass patch with single flower | | | | | |
| farm | farm, red barn with cylindrical silo | | | | | |
| garden | garden, flower bed rectangle with fence corner | | | | | |
| beach | beach, sandy strip with striped umbrella | | | | | |
| coast | coast, meeting line of sand and ocean waves | | | | | |
| island | island, green oval in blue water with palm | | | | | |
| mountain | mountain, tall triangular peak with snow cap | | | | | |
| hill | hill, soft green rounded mound | | | | | |
| river | river, winding blue ribbon through green banks | | | | | |
| lake | lake, calm blue oval with shoreline | | | | | |
| sea | sea, blue waves with small sailboat silhouette | | | | | |
| land | land, green hill with single tree on brown base | | | | | |
| road | road, gray path with dashed center line | | | | | |
| street | street, paved road with building silhouettes sides | | | | | |
| path | path, dotted trail curving through grass | | | | | |
| bridge | bridge, simple arch over blue water | | | | | |
| door | door, wooden rectangle with handle and frame | | | | | |
| window | window, square frame with cross panes | | | | | |
| wall | wall, brick pattern rectangle, no context | | | | | |
| floor | floor, wooden plank pattern, perspective lines | | | | | |
| corner | corner, two walls meeting at right angle | | | | | |
| ground | ground, brown soil with grass tufts | | | | | |
| camp | camp, triangle tent beside small campfire | | | | | |
| book | book, open hardcover with visible page lines | | | | | |
| page | page, single paper sheet with corner fold | | | | | |
| letter | letter, sealed envelope with stamp corner | | | | | |
| card | card, rectangle with heart symbol center | | | | | |
| paper | paper, blank white sheet, slight curl edge | | | | | |
| picture | picture, framed artwork showing mountain | | | | | |
| image | image, simple picture frame with landscape | | | | | |
| photo | photo, instant print with thick white border | | | | | |
| map | map, folded paper with route line and pin | | | | | |
| sign | sign, rectangular board on post with arrow | | | | | |
| phone | phone, smartphone rectangle with screen glow | | | | | |
| computer | computer, monitor rectangle above keyboard | | | | | |
| tv | tv, flat screen rectangle on simple stand | | | | | |
| television | television, screen with rabbit ear antenna | | | | | |
| radio | radio, vintage box with speaker grid and antenna | | | | | |
| camera | camera, simple body with round lens and flash | | | | | |
| video | video, film strip segment with play triangle | | | | | |
| film | film, movie reel canister with unspooling strip | | | | | |
| movie | movie, clapperboard with classic stripes | | | | | |
| album | album, square cover with music note symbol | | | | | |
| music | single floating eighth note, simple | | | | | |
| song | musical notes flowing from simple mouth outline | | | | | |
| sound | speaker icon with concentric wave circles | | | | | |
| voice | simple mouth with sound wave lines | | | | | |
| money | green paper bill with dollar sign | | | | | |
| cash | stack of bills held by paper clip | | | | | |
| gold | gold, shiny rectangular bar with highlight | | | | | |
| silver | silver, round coin with metallic reflection | | | | | |
| gift | gift, wrapped box with ribbon bow on top | | | | | |
| cup | cup, ceramic mug with handle and steam line | | | | | |
| glass | glass, transparent cylinder with water line | | | | | |
| box | box, closed cardboard cube with tape seam | | | | | |
| bag | bag, simple tote with two handles | | | | | |
| clothes | clothes, shirt and pants on hanger | | | | | |
| bed | bed, rectangle with pillow and blanket edge | | | | | |
| chair | chair, four legs with backrest, side view | | | | | |
| table | table, rectangular top with four simple legs | | | | | |
| seat | seat, round stool with three legs | | | | | |
| block | block, wooden cube with letter A on face | | | | | |
| piece | piece, single jigsaw puzzle tab and socket | | | | | |
| net | net, simple mesh pattern inside oval frame | | | | | |
| ring | ring, simple band circle with small gem dot | | | | | |
| machine | machine, large gear with attached lever | | | | | |
| iron | iron, classic clothes iron with steam holes | | | | | |
| water | water, single glossy teardrop droplet shape | | | | | |
| fire | fire, stylized orange-yellow flame pointing up | | | | | |
| air | swirling wind lines lifting a single leaf | | | | | |
| earth | earth, simple globe with green continent blobs | | | | | |
| sun | sun, bright yellow circle with triangular rays | | | | | |
| moon | moon, crescent shape with soft crater dots | | | | | |
| star | star, five-pointed shape with bold outline | | | | | |
| sky | sky, blue background with one fluffy white cloud | | | | | |
| cloud | cloud, single fluffy white puff, soft edges | | | | | |
| wind | wind, curved motion lines blowing a flag | | | | | |
| rain | rain, cloud with straight vertical drop lines | | | | | |
| snow | snow, symmetrical six-arm snowflake design | | | | | |
| ice | ice, transparent blue cube with highlight | | | | | |
| rock | rock, gray boulder with rough jagged outline | | | | | |
| stone | stone, smooth gray pebble, oval shape | | | | | |
| sand | sand, texture patch with small footprints | | | | | |
| tree | tree, brown trunk with round green canopy | | | | | |
| plant | plant, green leafy top in simple pot | | | | | |
| flower | flower, single colorful bloom with stem | | | | | |
| grass | grass, cluster of green blades, simple | | | | | |
| wood | wood, stack of three cylindrical logs | | | | | |
| animal | animal, generic friendly four-legged creature | | | | | |
| dog | dog, sitting with floppy ears and wagging tail | | | | | |
| cat | cat, sitting with pointed ears and whiskers | | | | | |
| fish | fish, side view with dorsal fin and tail | | | | | |
| bird | bird, perched with folded wings and beak | | | | | |
| bear | bear, sitting with round ears and snout | | | | | |
| horse | horse, side profile with mane and tail | | | | | |
| car | car, sedan side view with two wheels visible | | | | | |
| bus | bus, long rectangular vehicle with multiple windows | | | | | |
| van | van, boxy delivery vehicle with side sliding door | | | | | |
| train | train, locomotive front view with smokestack | | | | | |
| plane | plane, side view with wings and propeller | | | | | |
| aircraft | aircraft, commercial jet with wing engines | | | | | |
| ship | ship, large vessel with multiple decks | | | | | |
| boat | boat, small rowboat with two oars | | | | | |
| bike | bike, two wheels connected by triangle frame | | | | | |
| food | food, plate with colorful simple meal portions | | | | | |
| dinner | dinner, plate with meat slice and vegetables | | | | | |
| tea | tea, teacup on saucer with steam rising | | | | | |
| sweet | sweet, cupcake with frosting and sprinkles | | | | | |
| day | bright yellow sun in clear blue circle | | | | | |
| night | dark blue circle with crescent moon and stars | | | | | |
| morning | sun rising over horizon with soft rays | | | | | |
| season | circle divided into four: sun leaf snowflake flower | | | | | |
| summer | bright sun above palm tree and beach ball | | | | | |
| winter | snowflake falling on bare tree branches | | | | | |
| spring | green sprout pushing through soil with sun | | | | | |
| weather | cloud overlapping sun and raindrops together | | | | | |
| time | round clock face with hands pointing to three | | | | | |
| year | calendar page with single date circled | | | | | |
| weekend | calendar with Saturday and Sunday marked | | | | | |
| game | game, two colorful dice showing different numbers | | | | | |
| party | party, cone hat with confetti dots around | | | | | |
| fun | smiling face surrounded by colorful confetti | | | | | |
| story | story, open book with magical sparkles rising | | | | | |
| art | artist palette with brush and paint blobs | | | | | |
| color | simple rainbow arc with distinct bands | | | | | |
| choice | two thick arrows diverging from one point | | | | | |
| match | soccer ball between two simple goal nets | | | | | |
| goal | goal, soccer net with ball inside | | | | | |
| victory | shiny trophy cup with ribbon banners | | | | | |
| test | paper sheet with large checkmark and lines | | | | | |
| class | green chalkboard with ABC written | | | | | |
| club | door sign with musical note symbol | | | | | |
| band | three simple musical instruments in row | | | | | |
| dance | figure with swirling motion lines around | | | | | |
| sport | basketball hoop with ball going through | | | | | |
| football | classic black and white soccer ball | | | | | |
| christmas | decorated tree with star on top | | | | | |
| birth | pair of baby footprints, simple outline | | | | | |
| love | heart shape with small cupid arrow through it | | | | | |
| heart | classic symmetrical red heart shape | | | | | |
| magic | magic, wand tip with sparkle star burst | | | | | |
| eyes | eyes, pair of simple cartoon eyes looking forward | | | | | |
| eye | eye, single cartoon eye with pupil and lash | | | | | |
| mouth | mouth, simple smiling lips outline only | | | | | |
| hair | hair, flowing locks without face attached | | | | | |
| skin | arm patch showing smooth skin tone | | | | | |
| arm | arm, human limb from shoulder to hand | | | | | |
| foot | foot, side view showing toes and arch | | | | | |
| brain | brain, simplified pink two-lobe outline | | | | | |
| do | hand pointing to checklist with checkmark | | | | | |
| see | eye with focus rays or simple binoculars | | | | | |
| go | forward arrow with stepping foot outline | | | | | |
| take | hand grasping and lifting small object | | | | | |
| say | mouth outline with simple sound wave | | | | | |
| come | arrow pointing toward viewer, welcoming gesture | | | | | |
| look | eyes with directional focus lines | | | | | |
| find | magnifying glass over hidden object | | | | | |
| give | two hands exchanging small object | | | | | |
| help | two hands clasped together supportively | | | | | |
| put | hand placing object down on surface | | | | | |
| show | open palm presenting object upward | | | | | |
| play | child figure kicking simple ball | | | | | |
| start | green play button triangle | | | | | |
| read | open book with finger following line | | | | | |
| stop | raised hand with palm facing out | | | | | |
| thank | two hands forming heart shape | | | | | |
| run | figure in dynamic sprint pose | | | | | |
| talk | two faces with speech bubble between | | | | | |
| wait | figure sitting beside simple clock | | | | | |
| ask | figure with question mark above head | | | | | |
| playing | child stacking colorful blocks | | | | | |
| turn | curved circular arrow indicating rotation | | | | | |
| win | hand holding gold medal ribbon | | | | | |
| leave | figure walking away from open door | | | | | |
| move | object with directional displacement arrow | | | | | |
| stay | figure standing firmly on ground line | | | | | |
| meet | two figures shaking hands | | | | | |
| check | bold green checkmark symbol | | | | | |
| bring | figure carrying object toward viewer | | | | | |
| return | curved arrow pointing back to start | | | | | |
| rest | figure reclining in simple chair | | | | | |
| cut | open scissors with snip action line | | | | | |
| hear | ear shape with incoming wave lines | | | | | |
| hold | two hands gently cradling object | | | | | |
| answer | raised hand ready to speak | | | | | |
| follow | series of footprints leading forward | | | | | |
| learn | lightbulb glowing above open book | | | | | |
| share | two hands splitting object equally | | | | | |
| eat | spoon lifting food toward mouth | | | | | |
| fall | object dropping with vertical motion lines | | | | | |
| stand | figure upright with feet planted | | | | | |
| save | shield protecting small figure | | | | | |
| release | hand opening to let object go | | | | | |
| walk | figure captured in mid-step stride | | | | | |
| cover | blanket draped over simple shape | | | | | |
| sleep | figure lying flat with closed eyes | | | | | |
| pick | hand selecting one item from two | | | | | |
| speak | mouth with microphone outline | | | | | |
| cross | figure walking on zebra crossing lines | | | | | |
| listen | ear tilted toward sound source | | | | | |
| write | hand holding pencil making mark | | | | | |
| build | hands stacking three blocks vertically | | | | | |
| travel | suitcase with luggage tag attached | | | | | |
| reach | arm stretching toward distant object | | | | | |
| choose | finger pointing at single option | | | | | |
| join | two puzzle pieces fitting together | | | | | |
| carry | figure holding object while walking | | | | | |
| drink | cup tilted toward lips | | | | | |
| agree | two thumbs up side by side | | | | | |
| sit | figure seated comfortably on chair | | | | | |
| protect | umbrella shielding figure from rain | | | | | |
| touch | index finger gently contacting surface | | | | | |
| appear | object materializing with sparkle effect | | | | | |
| grow | small plant transforming into tall plant | | | | | |
| wear | figure with highlighted clothing item | | | | | |
| enter | figure stepping through doorway | | | | | |
| finish | checkered racing flag waving | | | | | |
| serve | hand presenting plate with food | | | | | |
| catch | hands cupped to receive falling ball | | | | | |
| count | hand showing three raised fingers | | | | | |
| rise | sun moving upward over horizon line | | | | | |
| draw | pencil creating curved line on paper | | | | | |
| receive | open hands accepting wrapped gift | | | | | |
| spread | knife smoothing substance on bread | | | | | |
| throw | arm in overhand throwing motion | | | | | |
| ride | figure pedaling bicycle forward | | | | | |
| shut | hand pushing door closed | | | | | |
| pull | hand tugging on rope with tension lines | | | | | |
| fly | bird soaring with wings fully spread | | | | | |
| push | hand pressing object forward | | | | | |
| wake | alarm clock ringing beside bed | | | | | |
| raise | hand lifting object upward | | | | | |
| new | shiny object with sparkle highlight | | | | | |
| good | thumbs up hand gesture | | | | | |
| old | object with visible crack and wear | | | | | |
| high | arrow pointing straight up | | | | | |
| big | large solid circle | | | | | |
| different | circle and square side by side | | | | | |
| bad | thumbs down hand gesture | | | | | |
| small | small solid circle | | | | | |
| full | cup filled to the brim | | | | | |
| open | door swinging wide open | | | | | |
| white | white circle on light gray background | | | | | |
| young | green sprout emerging from soil | | | | | |
| black | black circle with thick white outline | | | | | |
| large | large solid square | | | | | |
| nice | gentle smiling face outline | | | | | |
| wrong | bold red X mark | | | | | |
| light | lamp emitting glow rays | | | | | |
| low | arrow pointing straight down | | | | | |
| happy | broad smiling face with curved eyes | | | | | |
| red | solid red apple shape | | | | | |
| short | short horizontal line | | | | | |
| clear | transparent glass droplet | | | | | |
| easy | simple feather floating down | | | | | |
| ready | checkmark inside circle | | | | | |
| strong | flexed bicep muscle outline | | | | | |
| fine | thin precise line segment | | | | | |
| beautiful | delicate butterfly with patterned wings | | | | | |
| cool | sunglasses with reflective shine | | | | | |
| round | perfect circle shape | | | | | |
| natural | green leaf with vein details | | | | | |
| blue | solid blue water droplet | | | | | |
| simple | minimalist single line shape | | | | | |
| hot | red thermometer rising high | | | | | |
| green | solid green leaf shape | | | | | |
| complete | finished puzzle circle | | | | | |
| normal | standard gray square | | | | | |
| cold | blue snowflake with sharp points | | | | | |
| dark | moon phase in shadow circle | | | | | |
| safe | shield with checkmark inside | | | | | |
| welcome | open arms gesture with smile | | | | | |
| funny | clown nose with red dot | | | | | |
| huge | giant circle with tiny reference dot | | | | | |
| positive | bold plus sign | | | | | |
| physical | simple dumbbell weight | | | | | |
| wide | wide horizontal rectangle | | | | | |
| active | lightning bolt shape | | | | | |
| heavy | stone weight on scale | | | | | |
| regular | grid of equal squares | | | | | |
| awesome | star burst explosion shape | | | | | |
| basic | unadorned cube shape | | | | | |
| clean | sparkling object with shine lines | | | | | |
| quick | fast forward double arrow | | | | | |
| closed | padlock with shackle down | | | | | |
| glad | beaming face with raised eyebrows | | | | | |
| broken | object split into two pieces | | | | | |
| favorite | item with small heart tag | | | | | |
| sick | thermometer with red line high | | | | | |
| fit | running shoe with checkmark | | | | | |
| slow | snail shell spiral shape | | | | | |
| square | perfect square with equal sides | | | | | |
| fresh | dewdrop on green leaf tip | | | | | |
| wild | animal paw print in dirt | | | | | |
| correct | green checkmark symbol | | | | | |
| sad | frowning face with tear drop | | | | | |
| healthy | bright red apple with leaf | | | | | |
| prepared | neatly packed backpack | | | | | |
| useful | multi-tool with visible blades | | | | | |
| wonderful | glowing magic wand tip | | | | | |
| alive | pulsing heart with motion lines | | | | | |
| lucky | four-leaf clover shape | | | | | |
| excellent | gold star with five points | | | | | |
| afraid | wide open eyes with raised brows | | | | | |
| dry | cracked earth texture patch | | | | | |
